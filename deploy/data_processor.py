import pandas as pd
import numpy as np

class TeslaDataProcessor:
    """特斯拉财务数据处理类"""
    
    def __init__(self):
        self.data = self.create_tesla_dataset()
        
    def create_tesla_dataset(self):
        """创建 Tesla 财务预测数据集"""
        
        # 1. 各地区历史收入数据
        regional_data = pd.DataFrame({
            '地区': ['美国', '中国', '欧洲', '亚太', '中东', '其他'],
            '2022': [405.53, 181.45, 80, 40, 15, 92.64],
            '2023': [452.8, 251.01, 100.41, 55.78, 20.08, 87.82],
            '2024': [438, 250.24, 104.26, 62.56, 20.85, 101.15]
        })

        # 2. 各地区收入预测 2025-2030
        forecast_data = pd.DataFrame({
            '地区': ['美国', '中国', '欧洲', '亚太', '中东', '其他'],
            '2025': [455.52, 267.76, 116.77, 75.07, 23.98, 107.62],
            '2026': [473.74, 286.5, 130.78, 90.08, 27.58, 114.51],
            '2027': [492.69, 306.56, 146.47, 108.1, 31.72, 121.84],
            '2028': [512.4, 328.02, 164.05, 129.72, 36.48, 129.64],
            '2029': [532.9, 350.98, 183.74, 155.66, 41.95, 137.94],
            '2030': [554.22, 375.55, 205.79, 186.79, 48.24, 146.77]
        })

        # 3. 传统业务预测
        traditional_business = pd.DataFrame({
            '年份': ['2022', '2023', '2024', '2025E', '2026E', '2027E', '2028E', '2029E', '2030E'],
            '汽车业务': [714.62, 824.19, 770.7, 800.02, 861.03, 941.62, 1029.43, 1124.95, 1228.7],
            '能源业务': [39.09, 60.35, 100.86, 144.23, 201.92, 282.69, 395.77, 554.08, 775.71],
            '服务业务': [60.91, 83.19, 105.34, 133, 167.58, 211.15, 266.05, 335.22, 422.38],
            '传统业务总计': [814.62, 967.73, 976.9, 1077.25, 1230.53, 1435.46, 1691.25, 2014.25, 2426.79]
        })

        # 4. 新增业务预测
        new_business = pd.DataFrame({
            '年份': ['2022', '2023', '2024', '2025E', '2026E', '2027E', '2028E', '2029E', '2030E'],
            'Optimus': [0, 0, 0, 0, 3, 20, 90, 200, 300],
            'Robotaxi': [0, 0, 0, 0, 0, 5, 80, 130, 200],
            '新业务总计': [0, 0, 0, 0, 3, 25, 170, 330, 500]
        })

        # 5. 最终合并预测
        total_forecast = pd.DataFrame({
            '年份': ['2022', '2023', '2024', '2025E', '2026E', '2027E', '2028E', '2029E', '2030E'],
            '传统业务': [814.62, 967.73, 976.9, 1077.25, 1230.53, 1435.46, 1691.25, 2014.25, 2426.79],
            '新增业务': [0, 0, 0, 0, 3, 25, 170, 330, 500],
            '总收入': [814.62, 967.73, 976.9, 1077.25, 1233.53, 1460.46, 1861.25, 2344.25, 2926.79],
            'YoY增长': ['-', '18.8%', '0.9%', '10.3%', '14.5%', '18.4%', '27.4%', '26.0%', '24.8%']
        })

        # 6. 2030业务结构
        business_structure_2030 = pd.DataFrame({
            '业务类型': ['汽车业务', '能源业务', '服务业务', 'Optimus', 'Robotaxi', '总计'],
            '收入_亿美元': [1228.7, 775.71, 422.38, 300, 200, 2926.79],
            '占比': ['42.0%', '26.5%', '14.4%', '10.3%', '6.8%', '100.0%'],
            'CAGR': ['8.1%', '40.2%', '26.0%', 'N/A', 'N/A', '20.0%']
        })

        # 7. 各地区增长率假设
        growth_assumptions = pd.DataFrame({
            '地区': ['美国', '中国', '欧洲', '亚太', '中东', '其他'],
            '2025增长率': ['4.0%', '7.0%', '12.0%', '20.0%', '15.0%', '6.4%'],
            '2026-2030_CAGR': ['4.0%', '7.0%', '12.0%', '20.0%', '15.0%', '6.4%'],
            '假设说明': ['成熟市场稳定增长', '竞争激烈但仍有增长', '政策驱动增长', 
                      '新兴市场高速增长', '石油转型需求', '多元化市场稳定增长']
        })

        return {
            'regional_data': regional_data,
            'forecast_data': forecast_data,
            'traditional_business': traditional_business,
            'new_business': new_business,
            'total_forecast': total_forecast,
            'business_structure_2030': business_structure_2030,
            'growth_assumptions': growth_assumptions
        }
    
    def get_complete_region_data(self):
        """获取完整的地区数据（历史+预测）"""
        # 合并历史数据
        historical = self.data['regional_data'].melt(
            id_vars=['地区'], 
            value_vars=['2022', '2023', '2024'],
            var_name='年份', 
            value_name='收入'
        )
        
        # 合并预测数据
        forecast = self.data['forecast_data'].melt(
            id_vars=['地区'],
            value_vars=['2025', '2026', '2027', '2028', '2029', '2030'],
            var_name='年份',
            value_name='收入'
        )
        
        # 合并数据
        complete = pd.concat([historical, forecast], ignore_index=True)
        complete['年份'] = pd.to_numeric(complete['年份'])
        complete['数据类型'] = complete['年份'].apply(
            lambda x: '历史数据' if x <= 2024 else '预测数据'
        )
        
        return complete
    
    def get_region_growth_rates(self):
        """计算各地区复合增长率"""
        regions = self.data['regional_data']['地区'].tolist()
        growth_data = []
        
        for region in regions:
            # 获取2024年收入
            start_data = self.data['regional_data']
            start_2024 = start_data.loc[start_data['地区'] == region, '2024'].values[0]
            
            # 获取2030年收入
            forecast_data = self.data['forecast_data']
            end_2030 = forecast_data.loc[forecast_data['地区'] == region, '2030'].values[0]
            
            # 计算CAGR
            years = 6  # 2024到2030是6年
            cagr = ((end_2030 / start_2024) ** (1/years) - 1) * 100
            
            growth_data.append({
                '地区': region,
                '2024收入': round(start_2024, 2),
                '2030收入': round(end_2030, 2),
                'CAGR': round(cagr, 1)
            })
        
        return pd.DataFrame(growth_data)
    
    def get_business_growth_rates(self):
        """计算各业务增长率"""
        business_data = self.data['traditional_business']
        growth_data = []
        
        businesses = ['汽车业务', '能源业务', '服务业务']
        
        for business in businesses:
            # 获取2024年收入
            start_2024 = business_data.loc[business_data['年份'] == '2024', business].values[0]
            
            # 获取2030年收入
            end_2030 = business_data.loc[business_data['年份'] == '2030E', business].values[0]
            
            # 计算CAGR
            years = 6
            cagr = ((end_2030 / start_2024) ** (1/years) - 1) * 100
            
            growth_data.append({
                '业务类型': business,
                '2024收入': round(start_2024, 2),
                '2030收入': round(end_2030, 2),
                'CAGR': round(cagr, 1)
            })
        
        return pd.DataFrame(growth_data)
    
    def get_year_on_year_growth(self):
        """计算逐年增长率"""
        df = self.data['total_forecast'].copy()
        
        # 提取数字部分
        df['YoY数值'] = df['YoY增长'].replace('-', '0%').str.rstrip('%').astype(float)
        
        return df[['年份', 'YoY数值']].rename(columns={'YoY数值': '增长率%'})
    
    def get_regional_forecast_table(self, year):
        """获取特定年份的地区预测数据表"""
        if str(year) in ['2022', '2023', '2024']:
            df = self.data['regional_data'][['地区', str(year)]].copy()
            df = df.rename(columns={str(year): '收入'})
        elif str(year) in ['2025', '2026', '2027', '2028', '2029', '2030']:
            df = self.data['forecast_data'][['地区', str(year)]].copy()
            df = df.rename(columns={str(year): '收入'})
        else:
            df = pd.DataFrame(columns=['地区', '收入'])
        
        df['收入'] = df['收入'].round(2)
        df = df.sort_values('收入', ascending=False)
        
        return df
    
    def get_top_regions(self, year, n=3):
        """获取指定年份收入最高的地区"""
        df = self.get_regional_forecast_table(year)
        return df.head(n).to_dict('records')

# 创建全局数据处理器实例
tesla_data = TeslaDataProcessor()
