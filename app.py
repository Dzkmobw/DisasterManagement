from flask import Flask, render_template
import pandas as pd
from process_data import create_region_csv


app = Flask(__name__)

# 编码字典
SOURCE_CODES = {
    # 业务报送数据
    "100": "前方地震应急指挥部",
    "101": "后方地震应急指挥部",
    "120": "应急指挥技术系统",
    "121": "社会服务工程应急救援系统",
    "140": "危险区预评估工作组",
    "141": "地震应急指挥技术协调组",
    "142": "震后政府信息支持工作项目组",
    "180": "灾情快速上报接收处理系统",
    "181": "地方地震局应急信息服务相关技术系统",
    "199": "其他",  
    
    # 泛在感知数据
    "200": "互联网感知",
    "201": "通信网感知",
    "202": "舆情网感知",
    "203": "电力系统感知",
    "204": "交通系统感知",
    "205": "其他",  
    
    # 其他数据
    "300": "其他数据"  
}

CARRIER_CODES = {
    "0": "文字", "1": "图像", "2": "音频", "3": "视频","4": "其他"}

    # 更新后的灾情信息分类字典
CATEGORY_CODES ={
    "1": "震情",            
    "2": "人员伤亡及失踪",  
    "3": "房屋破坏", 
    "4": "生命线工程灾情",
    "5": "次生灾害"
}

SUBCATEGORY_CODES = {
    # 震情
    "101": "震情信息", 

    # 人员伤亡及失踪
    "201": "死亡",
    "202": "受伤",
    "203": "失踪",

    # 房屋破坏
    "301": "土木",
    "302": "砖木",
    "303": "砖混",
    "304": "框架",
    "305": "其他",

    # 生命线工程灾情
    "401": "交通",
    "402": "供水",
    "403": "输油",
    "404": "燃气",
    "405": "电力",
    "406": "通信",
    "407": "水利",

    # 次生灾害
    "501": "崩塌",
    "502": "滑坡",
    "503": "泥石流",
    "504": "岩溶塌陷",
    "505": "地裂缝",
    "506": "地面沉降",
    "507": "其他"  
}

TAG_CODES = {
    # 震情
    "1001": "地理位置",   
    "1002": "时间",
    "1003": "震级",
    "1004": "震源深度",
    "1005": "烈度",  

    # 人员伤亡及失踪
    "2001": "受灾人数", 
    "2002": "受灾程度",  

    # 房屋破坏
    "3001": "一般损坏面积",  
    "3002": "严重损坏面积",  
    "3003": "受灾程度",    

    # 生命线工程灾情
    "4001": "受灾设施数",  
    "4002": "受灾范围",    
    "4003": "受灾程度",   

    # 次生灾害
    "5001": "灾害损失",     
    "5002": "灾害范围",     
    "5003": "受灾程度",     
}

# 读取地理码 CSV 文件
geo_df = pd.read_csv('region_code.csv')

def get_location_from_geo_code(geo_info):
    matched_row = geo_df[geo_df['id'].astype(str) == str(geo_info)]
    if not matched_row.empty:
        province = matched_row['province'].values[0]
        city = matched_row['city'].values[0]
        county = matched_row['county'].values[0]
        town = matched_row['town'].values[0]
        village = matched_row['village'].values[0]
        return f"{province}{city}{county}{town}{village}"
    else:
        return "未知位置"

# 解码函数
def decode_id(row_id, description):
    try:
        # 分段解析
        geo_info = row_id[0:12]        # 地理信息
        time_info = row_id[12:26]      # 时间信息
        source_code = row_id[26:29]    # 来源编码
        carrier_code = row_id[29:30]   # 载体编码
        category_code = row_id[30:31]  # 灾害大类
        subcategory_code = row_id[31:33]  # 灾害子类
        tag_code = row_id[33:36]       # 灾害指标
        full_tag_code = category_code + tag_code
        full_subcategory_code = category_code + subcategory_code

        # 字段解码
        location = get_location_from_geo_code(geo_info)
        time = f"{time_info[:4]}-{time_info[4:6]}-{time_info[6:8]} {time_info[8:10]}:{time_info[10:12]}:{time_info[12:14]}"
        source = SOURCE_CODES.get(source_code, source_code)
        carrier = CARRIER_CODES.get(carrier_code, carrier_code)
        category = CATEGORY_CODES.get(category_code, category_code)
        subcategory = SUBCATEGORY_CODES.get(full_subcategory_code, full_subcategory_code)
        tag = TAG_CODES.get(full_tag_code, full_tag_code)

        return {
            "编号": row_id,
            "参考位置": location,
            "时间": time,
            "数据源": source,
            "数据载体": carrier,
            "分类":category,
            "子类": subcategory,
            "标签": tag,
            "描述": description
        }
    except Exception as e:
        print(f"Error decoding ID {row_id}: {e}")
        return {"编号": row_id, "错误": "解析失败"}

@app.route('/')
def index():
    input_file = 'data.xlsx'
    #output_file = 'decoded_data.xlsx'

    try:
        # 读取 Excel 文件
        df = pd.read_excel(input_file)

        if 'id' not in df.columns:
            return "Error: 输入文件中未找到id列，请检查文件格式。"

        # 解码数据
        decoded_data = [decode_id(str(row['id']), row['描述']) for _, row in df.iterrows()]
        #decoded_df = pd.DataFrame(decoded_data)
        #decoded_df.to_excel(output_file, index=False)


        return render_template('index.html', data=decoded_data)
    except Exception as e:
        return f"Error processing data: {e}"
    
@app.cli.command("create")
def create_csv():
    create_region_csv()

if __name__ == '__main__':
    app.run(debug=True)