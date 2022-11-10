import pandas as pd
import numpy as np
import scipy.stats as stats


def correlation_analysis_target_acc_vs_ensemble_weight(accuracies_df: pd.DataFrame,
                                                       ensemble_weights_df: pd.DataFrame,
                                                       alternative_hypothesis: str = 'two-sided',
                                                       avg_seeds_before_corr_analysis: bool = False) -> pd.DataFrame:
    """Perform a correlation analysis with `scipy.stats.pearsonr` between target accuracy and ensemble weights.

    Args:
        accuracies_df (pd.DataFrame): Dataframe with source and target accuracies.
        ensemble_weights_df (pd.DataFrame): Dataframe with ensemble weights.
        alternative_hypothesis (str, optional): The alternative hypothesis. Defaults to 'two-sided'.
        avg_seeds_before_corr_analysis (bool, optional): If True, average target accuracy and ensemble weights over seeds 
                                                         before running the correlation analysis. Defaults to False.

    Returns:
        pd.DataFrame: The correlation results for each domains pair (src + target) and 
                      ensemble method as rows and the correlation coefficient, p-value and confidience interval as columns.
    """
    if avg_seeds_before_corr_analysis:
        # average across seeds
        acc_df = accuracies_df.groupby(level=['domains', 'domain']).mean()
        ew_df = ensemble_weights_df.groupby(level=['domains', 'ensemble_methods']).mean()
    else:
        acc_df = accuracies_df
        ew_df = ensemble_weights_df.swaplevel(0,1).swaplevel(1,2).sort_index(level=['domains','ensemble_methods'])

    # select all columns from ew_df in results_table and select only target accuracy
    target_acc_df = acc_df[ew_df.columns].xs(key='target', level='domain')

    # perform correlation analysis between target accuracy, and all rows n ensemble method
    ew_index = ew_df.index

    ew_avg_correlation_results_columns = ['corr_coeff', 'p_val', 'ci_low', 'ci_high']
    ew_avg_correlation_results = []
    for row_idx in ew_index: # row_index = (domains, ensemble_method, [seed])
        # data to measure correlation on
        if avg_seeds_before_corr_analysis:
            target_acc_row = target_acc_df.loc[row_idx[0]].to_numpy()
        else:
            target_acc_row = target_acc_df.loc[row_idx[0], row_idx[2]].to_numpy()
        ew_row = ew_df.loc[row_idx].to_numpy()
        
        pearson_corr_res = stats.pearsonr(target_acc_row, ew_row, alternative=alternative_hypothesis)
        ew_avg_correlation_results.append(
            np.array([pearson_corr_res, pearson_corr_res.confidence_interval()]).flatten())
    # results array
    ew_avg_correlation_results = np.array(ew_avg_correlation_results)
    # create result dataframe
    corr_res_df = pd.DataFrame(data=ew_avg_correlation_results,
                               columns=ew_avg_correlation_results_columns,
                               index=ew_index)
    return corr_res_df