import pandas as pd

def create_region_csv(input_file='region_code.xls', output_file='region_code.csv'):

    column_names = ['id', 'province', 'city', 'county', 'town', 'village']
    try:
        df = pd.read_excel(input_file, sheet_name=None, header=None, names=column_names, engine='xlrd')
        
        combined_df = pd.concat(df.values(), ignore_index=True)
        combined_df = combined_df.drop(0, axis=0).reset_index(drop=True)
        
        combined_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"所有工作表已合并并保存为 {output_file}")
    except Exception as e:
        print(f"错误: {e}")
