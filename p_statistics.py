import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

matplotlib.use('Agg')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']

def generate_statistics_plot(data_df, plot_path):
    data_df['日期'] = pd.to_datetime(data_df['时间']).dt.date  
    date_source_stats = data_df.groupby(['日期', '数据源']).size().reset_index(name='数量')

    plt.figure(figsize=(10, 6))
    sns.countplot(data=date_source_stats, x='日期', hue='数据源', palette='Set2')
    plt.title('日期与数据源的统计分布')
    plt.xlabel('日期')
    plt.ylabel('占比')
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
