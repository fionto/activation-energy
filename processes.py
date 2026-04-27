from scipy import stats
import pandas as pd
from models import LinearFit

def linear_fit(array_x: pd.Series, array_y: pd.Series) -> LinearFit:

    linear_stats = stats.linregress(array_x, array_y)

    return LinearFit(
        slope=linear_stats.slope,           # type: ignore
        intercept=linear_stats.intercept,   # type: ignore
        r_squared=linear_stats.rvalue**2,   # type: ignore
    )