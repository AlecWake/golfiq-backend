from datetime import timedelta

from sqlalchemy.orm import Session, selectinload

from app.db.models.hole_score import HoleScore
from app.db.models.round import Round
from app.db.models.round_stat import RoundStat
from app.db.models.user import User
from app.schemas.round_analytics import (
    MultiRoundAnalyticsSummaryResponse,
    RoundAnalyticsSummaryResponse,
)
from app.services.analytics_utils import average_or_zero
from app.services.round_service import get_user_round


DEFAULT_HOLE_PAR = 4


def _percentage(value: int, possible: int) -> float:
    if possible == 0:
        return 0.0

    return round((value / possible) * 100, 2)


def _score_counts(hole_scores: list[HoleScore]) -> tuple[int, int, int, int]:
    birdies = 0
    pars = 0
    bogeys = 0
    double_bogeys_or_worse = 0

    for hole_score in hole_scores:
        score_to_par = hole_score.strokes - DEFAULT_HOLE_PAR

        if score_to_par <= -1:
            birdies += 1
        elif score_to_par == 0:
            pars += 1
        elif score_to_par == 1:
            bogeys += 1
        else:
            double_bogeys_or_worse += 1

    return birdies, pars, bogeys, double_bogeys_or_worse


def get_round_analytics_summary(
    db: Session,
    current_user: User,
    round_id: int,
) -> RoundAnalyticsSummaryResponse:
    user_round = get_user_round(db, current_user, round_id)
    round_stat = (
        db.query(RoundStat).filter(RoundStat.round_id == user_round.id).first()
    )
    hole_scores = (
        db.query(HoleScore)
        .filter(HoleScore.round_id == user_round.id)
        .order_by(HoleScore.hole_number)
        .all()
    )

    if round_stat is not None:
        fairways_hit = round_stat.fairways_hit
        fairways_possible = round_stat.fairways_possible
        greens_in_regulation = round_stat.greens_in_regulation
        total_putts = round_stat.putts
        penalty_strokes = round_stat.penalties
    else:
        fairways_hit = sum(1 for hole_score in hole_scores if hole_score.fairway_hit)
        fairways_possible = len(hole_scores)
        greens_in_regulation = sum(
            1 for hole_score in hole_scores if hole_score.green_in_regulation
        )
        total_putts = sum(hole_score.putts for hole_score in hole_scores)
        penalty_strokes = sum(hole_score.penalty_strokes for hole_score in hole_scores)

    birdies, pars, bogeys, double_bogeys_or_worse = _score_counts(hole_scores)

    return RoundAnalyticsSummaryResponse(
        round_id=user_round.id,
        total_score=user_round.total_score,
        holes_played=user_round.holes_played,
        fairways_hit=fairways_hit,
        fairways_possible=fairways_possible,
        fairway_percentage=_percentage(fairways_hit, fairways_possible),
        greens_in_regulation=greens_in_regulation,
        gir_percentage=_percentage(greens_in_regulation, user_round.holes_played),
        total_putts=total_putts,
        penalty_strokes=penalty_strokes,
        average_score_per_hole=round(
            user_round.total_score / user_round.holes_played,
            2,
        ),
        birdies=birdies,
        pars=pars,
        bogeys=bogeys,
        double_bogeys_or_worse=double_bogeys_or_worse,
    )


def _stat_values_for_round(user_round: Round) -> tuple[int | None, int | None]:
    if user_round.stats is not None:
        return user_round.stats.putts, user_round.stats.penalties

    if user_round.hole_scores:
        return (
            sum(hole_score.putts for hole_score in user_round.hole_scores),
            sum(hole_score.penalty_strokes for hole_score in user_round.hole_scores),
        )

    return None, None


def _fairway_percentage_for_round(user_round: Round) -> float | None:
    if user_round.stats is not None:
        return _percentage(
            user_round.stats.fairways_hit,
            user_round.stats.fairways_possible,
        )

    if user_round.hole_scores:
        fairways_hit = sum(
            1 for hole_score in user_round.hole_scores if hole_score.fairway_hit
        )
        return _percentage(fairways_hit, len(user_round.hole_scores))

    return None


def _gir_percentage_for_round(user_round: Round) -> float | None:
    if user_round.stats is not None:
        return _percentage(
            user_round.stats.greens_in_regulation,
            user_round.holes_played,
        )

    if user_round.hole_scores:
        greens_in_regulation = sum(
            1
            for hole_score in user_round.hole_scores
            if hole_score.green_in_regulation
        )
        return _percentage(greens_in_regulation, len(user_round.hole_scores))

    return None


def get_multi_round_analytics_summary(
    db: Session,
    current_user: User,
) -> MultiRoundAnalyticsSummaryResponse:
    user_rounds = (
        db.query(Round)
        .options(selectinload(Round.stats), selectinload(Round.hole_scores))
        .filter(Round.user_id == current_user.id)
        .all()
    )

    if not user_rounds:
        return MultiRoundAnalyticsSummaryResponse(
            total_rounds=0,
            average_score=0.0,
            best_score=None,
            worst_score=None,
            average_putts=0.0,
            average_penalties=0.0,
            average_fairway_percentage=0.0,
            average_gir_percentage=0.0,
            total_holes_played=0,
            recent_rounds_count=0,
        )

    scores = [user_round.total_score for user_round in user_rounds]
    putt_totals: list[int] = []
    penalty_totals: list[int] = []
    fairway_percentages: list[float] = []
    gir_percentages: list[float] = []

    for user_round in user_rounds:
        putts, penalties = _stat_values_for_round(user_round)
        fairway_percentage = _fairway_percentage_for_round(user_round)
        gir_percentage = _gir_percentage_for_round(user_round)

        if putts is not None:
            putt_totals.append(putts)
        if penalties is not None:
            penalty_totals.append(penalties)
        if fairway_percentage is not None:
            fairway_percentages.append(fairway_percentage)
        if gir_percentage is not None:
            gir_percentages.append(gir_percentage)

    latest_round_date = max(user_round.round_date for user_round in user_rounds)
    recent_cutoff = latest_round_date - timedelta(days=30)
    recent_rounds_count = sum(
        1 for user_round in user_rounds if user_round.round_date >= recent_cutoff
    )

    return MultiRoundAnalyticsSummaryResponse(
        total_rounds=len(user_rounds),
        average_score=average_or_zero(scores),
        best_score=min(scores),
        worst_score=max(scores),
        average_putts=average_or_zero(putt_totals),
        average_penalties=average_or_zero(penalty_totals),
        average_fairway_percentage=average_or_zero(fairway_percentages),
        average_gir_percentage=average_or_zero(gir_percentages),
        total_holes_played=sum(user_round.holes_played for user_round in user_rounds),
        recent_rounds_count=recent_rounds_count,
    )
