from sqlalchemy.orm import Session

from app.db.models.hole_score import HoleScore
from app.db.models.round_stat import RoundStat
from app.db.models.user import User
from app.schemas.round_analytics import RoundAnalyticsSummaryResponse
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
