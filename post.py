"""
根据 UUID 查询用户姓名 + 帖子标题 + 帖子内容 + 图片
数据库：阿里云 RDS MySQL
Flask API 版本 - 提供 HTTP 接口供前端调用
"""
from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

# ===================== 数据库配置 =====================
DB_CONFIG = {
    "host": "rm-bp1kp895v5860947b4o.mysql.rds.aliyuncs.com",
    "user": "test_lixingshuai",
    "password": "tesT951A",
    "database": "jianlun_web",
    "port": 3306,
    "charset": "utf8mb4"
}

# ===================== UUID 与姓名映射配置 =====================
# 在这里手动配置UUID和对应的真实姓名
UUID_NAME_MAPPING = {
    "c614cc138169a53fb8381493a93082b4": "朱锐",
    "530bffc0244327f06539a27f8c54d266": "吴俐伽",
    "6ab3ba79b5abf19b6c39e91922e6aff8": "杨泽文",
    "bafa832d01a876f08963af86564bba39": "朱艺楠",
    "33b24e2b1859b8445c0266172c7da4db": "汪晓威",
    "1b0aa829b895450e9e59c35d8710c6fd": "李政霖",
    "a7315818c33906e1b3af158d6c8b2bab": "李爽",
    "1b8e8fa91d4e7b14aadc8e62c0444d88": "王过",
    "1c3be36c7f378e619a242da0e92deec2": "冯连华",
    "e55f9aa3237cca06e019a9123ede8375": "陈云",
    "ed578d1fc861d6cc3e6e0ba69675864b": "李昱",
    "3412d2b784ec7c62b43b6229a6a96636": "聂博文",
    "e3a14d94b2f83fa77a22a46c71bc41ba": "邓宇海",
    "f4468ae37179bc449733e88772af2529": "刘雨轩",
    "37be7faf483a9354a3ffaa09bf0b1a2a": "李兴帅",
    "a294499ca951b32d037d7f98951e7ac4": "程丹丹",
    "3d94dd8a056ff70f8b1569874abe4a88": "刘昊天",
    "b70f214aedeb1cfb4b53e96f34daeadf": "刘祥宇",
    "4e7d3957eb03468089ee5a0158b65c23": "周重天",
    "3c1e54c9f89b4b44d3b99aeac30e3a98": "吴雨桁",
    "cc3a23dbf9a243220193bd2fbe91bbfc": "陈达",
    "2cffa20a0d5660afe1702125c6f99b64": "杨峥芃",
    "23e449584dbb4c9f1e553e4784989b36": "董晓峰",
    "b967ef3c53695dd3b2edfd575f36716c": "庞天傲",
    "26140ab161208d644798e74810f0c011": "胡钧耀",
}

# 获取所有UUID列表
DEFAULT_UUID_LIST = list(UUID_NAME_MAPPING.keys())

# ===================== 基础 SQL 查询语句 =====================
BASE_SQL = """
SELECT
    u.uuid,
    p.title,
    p.created_at,
    pc.content,
    pc.img_url
FROM
    inf_user u
INNER JOIN inf_post p ON u.id = p.user_id
LEFT JOIN inf_post_content pc ON p.id = pc.post_id
WHERE
    u.uuid = %s
    AND p.status = 1
"""


def execute_query(uuid_list, start_date=None, end_date=None):
    """执行查询并返回结果"""
    results = []
    total_count = 0
    
    # 处理时间范围
    start_time = f"{start_date} 00:00:00" if start_date else None
    end_time = f"{end_date} 23:59:59" if end_date else None
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        
        for uuid in uuid_list:
            query = BASE_SQL
            params = (uuid,)
            
            # 添加时间范围条件
            time_conditions = []
            if start_time:
                time_conditions.append("p.created_at >= %s")
                params = params + (start_time,)
            if end_time:
                time_conditions.append("p.created_at <= %s")
                params = params + (end_time,)
            
            if time_conditions:
                query = BASE_SQL.replace(
                    "AND p.status = 1",
                    "AND p.status = 1 AND " + " AND ".join(time_conditions)
                )
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    total_count += 1
                    # 转换datetime对象为字符串
                    if row.get('created_at'):
                        row['created_at'] = row['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    # 使用手动配置的姓名映射
                    uuid = row.get('uuid', '')
                    row['realname'] = UUID_NAME_MAPPING.get(uuid, '未知')
                    row['index'] = total_count
                    
                    # 数据直接返回，由JSON序列化处理
                    
                    results.append(row)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        return {"error": str(e)}, 0
    
    return results, total_count


@app.route('/api/query', methods=['GET', 'POST'])
def query_posts():
    """API接口：查询帖子数据"""
    try:
        # 获取请求参数
        if request.method == 'POST':
            data = request.json or {}
        else:
            data = request.args.to_dict()
        
        # 获取UUID列表
        uuid_list = data.get('uuids', DEFAULT_UUID_LIST)
        if isinstance(uuid_list, str):
            # 如果是单个UUID，转换为列表
            uuid_list = [uuid_list]
        
        # 获取时间范围
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        
        # 执行查询
        results, total_count = execute_query(uuid_list, start_date, end_date)
        
        if isinstance(results, dict) and "error" in results:
            return jsonify({
                "success": False,
                "message": results["error"],
                "data": [],
                "total": 0
            }), 500
        
        return jsonify({
            "success": True,
            "message": "查询成功",
            "data": results,
            "total": total_count,
            "time_range": {
                "start": start_date if start_date else None,
                "end": end_date if end_date else None
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "data": [],
            "total": 0
        }), 500


@app.route('/')
def index():
    """返回前端看板页面"""
    return r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>减论科技员工发帖详情</title>
    <link href="https://cdn.bootcdn.net/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.bootcdn.net/ajax/libs/bootstrap-icons/1.8.1/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #4a90e2;
            --secondary-color: #f5f7fa;
            --accent-color: #67c23a;
            --text-color: #2c3e50;
            --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .container {
            max-width: 1400px;
        }
        
        .header-card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: var(--card-shadow);
        }
        
        .title {
            color: var(--text-color);
            font-size: 28px;
            font-weight: 700;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .title i {
            color: var(--primary-color);
        }
        
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: var(--card-shadow);
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-4px);
        }
        
        .stat-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-bottom: 12px;
        }
        
        .stat-icon.primary {
            background: rgba(74, 144, 226, 0.1);
            color: var(--primary-color);
        }
        
        .stat-icon.success {
            background: rgba(103, 194, 58, 0.1);
            color: var(--accent-color);
        }
        
        .stat-icon.info {
            background: rgba(64, 158, 255, 0.1);
            color: #409eff;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: var(--text-color);
        }
        
        .stat-label {
            color: #909399;
            font-size: 14px;
            margin-top: 4px;
        }
        
        .filter-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: var(--card-shadow);
        }
        
        .employee-stats-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: var(--card-shadow);
        }
        
        .employee-stats-header {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .employee-stats-content {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }
        
        .employee-stat-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eef3 100%);
            border-radius: 8px;
            min-width: 160px;
        }
        
        .employee-stat-item .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary-color) 0%, #67c23a 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 14px;
        }
        
        .employee-stat-item .info {
            flex: 1;
        }
        
        .employee-stat-item .name {
            font-size: 14px;
            font-weight: 500;
            color: var(--text-color);
        }
        
        .employee-stat-item .count {
            font-size: 18px;
            font-weight: 700;
            color: var(--primary-color);
        }
        
        .employee-stat-item .count.zero {
            color: #909399;
        }
        
        .filter-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .data-card {
            background: white;
            border-radius: 12px;
            box-shadow: var(--card-shadow);
            overflow: hidden;
        }
        
        .data-card-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, #67c23a 100%);
            color: white;
            padding: 16px 20px;
            font-size: 18px;
            font-weight: 600;
        }
        
        .table-responsive {
            padding: 0;
        }
        
        .table {
            margin: 0;
        }
        
        .table thead th {
            background: #f5f7fa;
            border: none;
            padding: 14px 12px;
            font-weight: 600;
            color: #606266;
            font-size: 14px;
        }
        
        .table tbody td {
            padding: 14px 12px;
            vertical-align: middle;
            border-color: #ebeef5;
            font-size: 14px;
        }
        
        .table tbody tr:hover {
            background: #f5f7fa;
        }
        
        .uuid-cell {
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 12px;
            color: #909399;
            max-width: 120px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .title-cell {
            font-weight: 500;
            color: var(--primary-color);
            max-width: 250px;
        }
        
        .content-cell {
            max-width: 500px;
            min-width: 200px;
        }
        
        .content-cell.truncated {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            cursor: pointer;
            max-width: 500px;
        }
        
        .content-cell.expanded {
            white-space: normal;
            word-break: break-all;
            max-width: 600px;
        }
        
        .content-toggle {
            color: var(--primary-color);
            cursor: pointer;
            font-size: 12px;
            margin-left: 8px;
        }
        
        .content-toggle:hover {
            text-decoration: underline;
        }
        
        .time-cell {
            color: #909399;
            font-size: 13px;
        }
        
        .img-thumb {
            width: 60px;
            height: 60px;
            object-fit: cover;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .img-thumb:hover {
            transform: scale(1.1);
        }
        
        .empty-state {
            padding: 60px 20px;
            text-align: center;
            color: #909399;
        }
        
        .empty-state i {
            font-size: 64px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 60px;
        }
        
        .spinner-border {
            width: 3rem;
            height: 3rem;
        }
        
        .modal-img {
            max-width: 100%;
            max-height: 80vh;
        }
        
        .btn-primary {
            background: var(--primary-color);
            border: none;
            padding: 10px 24px;
            border-radius: 8px;
            font-weight: 500;
        }
        
        .btn-primary:hover {
            background: #3a80d2;
        }
        
        .form-control, .form-select {
            border-radius: 8px;
            border: 1px solid #dcdfe6;
            padding: 10px 14px;
        }
        
        .form-control:focus, .form-select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
        }
        
        .time-range-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 标题 -->
        <div class="header-card">
            <h1 class="title">
                <i class="bi bi-grid-3x3-gap-fill"></i>
                减论科技员工发帖详情
            </h1>
        </div>
        
        <!-- 统计卡片 -->
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-icon primary">
                    <i class="bi bi-collection"></i>
                </div>
                <div class="stat-value" id="totalCount">0</div>
                <div class="stat-label">总帖子数</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon success">
                    <i class="bi bi-people"></i>
                </div>
                <div class="stat-value" id="userCount">0</div>
                <div class="stat-label">发帖人数</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon warning">
                    <i class="bi bi-person-plus"></i>
                </div>
                <div class="stat-value" id="employeeCount">0</div>
                <div class="stat-label">员工数量</div>
            </div>
        </div>
        
        <!-- 筛选条件 -->
        <div class="filter-card">
            <div class="filter-title">
                <i class="bi bi-funnel"></i>
                筛选条件
            </div>
            <div class="row g-3 align-items-end">
                <div class="col-md-4">
                    <label class="form-label">起始日期</label>
                    <input type="date" class="form-control" id="startDate" placeholder="选择开始日期">
                </div>
                <div class="col-md-4">
                    <label class="form-label">结束日期</label>
                    <input type="date" class="form-control" id="endDate" placeholder="选择结束日期">
                </div>
                <div class="col-md-4">
                    <button class="btn btn-primary w-100" onclick="loadData()">
                        <i class="bi bi-search"></i> 查询数据
                    </button>
                </div>
            </div>
        </div>

        <!-- 员工发帖统计 -->
        <div class="employee-stats-card" id="employeeStatsCard">
            <div class="employee-stats-header d-flex justify-content-between align-items-center">
                <span><i class="bi bi-bar-chart-line"></i> 员工发帖统计</span>
                <span class="time-range-badge" id="employeeTimeRangeBadge" style="display: none;">
                    <i class="bi bi-calendar-range"></i>
                    <span id="employeeTimeRangeText"></span>
                </span>
            </div>
            <div class="employee-stats-content" id="employeeStatsContent">
                <!-- 动态生成员工发帖统计 -->
            </div>
        </div>
        
        <!-- 数据表格 -->
        <div class="data-card">
            <div class="data-card-header d-flex justify-content-between align-items-center">
                <span><i class="bi bi-list-ul"></i> 查询结果</span>
                <span class="time-range-badge" id="timeRangeBadge" style="display: none;">
                    <i class="bi bi-calendar-range"></i>
                    <span id="timeRangeText"></span>
                </span>
            </div>
            <div class="table-responsive" id="tableContainer">
                <div class="loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 图片预览模态框 -->
    <div class="modal fade" id="imgModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content">
                <div class="modal-body text-center">
                    <img src="" alt="" class="modal-img" id="modalImg">
                </div>
            </div>        </div>
    </div>
    
    <script src="https://cdn.bootcdn.net/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js"></script>
    <script>
        // 默认加载数据
        document.addEventListener('DOMContentLoaded', function() {
            loadData();
        });
        
        // 按回车键触发查询
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                loadData();
            }
        });
        
        function loadData() {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            
            // 显示时间范围
            const timeRangeBadge = document.getElementById('timeRangeBadge');
            const timeRangeText = document.getElementById('timeRangeText');
            const employeeTimeRangeBadge = document.getElementById('employeeTimeRangeBadge');
            const employeeTimeRangeText = document.getElementById('employeeTimeRangeText');
            const timeRange = (startDate || '开始') + ' ~ ' + (endDate || '结束');
            
            if (startDate || endDate) {
                timeRangeBadge.style.display = 'inline-flex';
                timeRangeText.textContent = timeRange;
                employeeTimeRangeBadge.style.display = 'inline-flex';
                employeeTimeRangeText.textContent = timeRange;
            } else {
                timeRangeBadge.style.display = 'none';
                employeeTimeRangeBadge.style.display = 'none';
            }
            
            // 显示加载状态，使用DOM方法构建
            const tableContainer = document.getElementById('tableContainer');
            
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'loading';
            
            const spinnerDiv = document.createElement('div');
            spinnerDiv.className = 'spinner-border text-primary';
            spinnerDiv.setAttribute('role', 'status');
            
            const spinnerText = document.createElement('span');
            spinnerText.className = 'visually-hidden';
            spinnerText.textContent = 'Loading...';
            
            spinnerDiv.appendChild(spinnerText);
            loadingDiv.appendChild(spinnerDiv);
            
            tableContainer.innerHTML = '';
            tableContainer.appendChild(loadingDiv);

            // 调用API
            fetch('/api/query?start_date=' + (startDate || '') + '&end_date=' + (endDate || ''))
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        renderTable(result.data);
                        updateStats(result.data);
                    } else {
                        // 使用DOM方法安全地构建错误消息
                        const errorDiv = document.createElement('div');
                        errorDiv.className = 'empty-state';
                        
                        const icon = document.createElement('i');
                        icon.className = 'bi bi-exclamation-triangle';
                        errorDiv.appendChild(icon);
                        
                        const p = document.createElement('p');
                        p.textContent = '查询失败: ' + (result.message || '');
                        errorDiv.appendChild(p);
                        
                        tableContainer.innerHTML = '';
                        tableContainer.appendChild(errorDiv);
                    }
                })
                .catch(error => {
                    // 使用DOM方法安全地构建错误消息
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'empty-state';
                    
                    const icon = document.createElement('i');
                    icon.className = 'bi bi-wifi-off';
                    errorDiv.appendChild(icon);
                    
                    const p = document.createElement('p');
                    p.textContent = '网络错误: ' + (error.message || '');
                    errorDiv.appendChild(p);
                    
                    tableContainer.innerHTML = '';
                    tableContainer.appendChild(errorDiv);
                });
        }
        
        function updateStats(data) {
            document.getElementById('totalCount').textContent = data.length;
            
            // 统计用户数（去重）
            const uniqueUsers = new Set(data.map(item => item.uuid));
            document.getElementById('userCount').textContent = uniqueUsers.size;
            
            // 设置员工数量（UUID总数）
            document.getElementById('employeeCount').textContent = 25;
            
            // 员工发帖统计
            const employeeStatsContent = document.getElementById('employeeStatsContent');
            if (!employeeStatsContent) return;
            
            // 统计每个员工的发帖次数
            const employeePostCounts = {};
            data.forEach(item => {
                const uuid = item.uuid;
                const realname = item.realname;
                if (uuid) {
                    if (!employeePostCounts[uuid]) {
                        employeePostCounts[uuid] = { realname: realname, count: 0 };
                    }
                    employeePostCounts[uuid].count++;
                }
            });
            
            // 生成员工统计HTML
            let statsHtml = '';
            // 员工名单（与后端UUID_NAME_MAPPING保持一致）
            const employeeList = [
                { uuid: "c614cc138169a53fb8381493a93082b4", name: "朱锐" },
                { uuid: "530bffc0244327f06539a27f8c54d266", name: "吴俐伽" },
                { uuid: "6ab3ba79b5abf19b6c39e91922e6aff8", name: "杨泽文" },
                { uuid: "bafa832d01a876f08963af86564bba39", name: "朱艺楠" },
                { uuid: "33b24e2b1859b8445c0266172c7da4db", name: "汪晓威" },
                { uuid: "1b0aa829b895450e9e59c35d8710c6fd", name: "李政霖" },
                { uuid: "a7315818c33906e1b3af158d6c8b2bab", name: "李爽" },
                { uuid: "1b8e8fa91d4e7b14aadc8e62c0444d88", name: "王过" },
                { uuid: "1c3be36c7f378e619a242da0e92deec2", name: "冯连华" },
                { uuid: "e55f9aa3237cca06e019a9123ede8375", name: "陈云" },
                { uuid: "ed578d1fc861d6cc3e6e0ba69675864b", name: "李昱" },
                { uuid: "3412d2b784ec7c62b43b6229a6a96636", name: "聂博文" },
                { uuid: "e3a14d94b2f83fa77a22a46c71bc41ba", name: "邓宇海" },
                { uuid: "f4468ae37179bc449733e88772af2529", name: "刘雨轩" },
                { uuid: "37be7faf483a9354a3ffaa09bf0b1a2a", name: "李兴帅" },
                { uuid: "a294499ca951b32d037d7f98951e7ac4", name: "程丹丹" },
                { uuid: "3d94dd8a056ff70f8b1569874abe4a88", name: "刘昊天" },
                { uuid: "b70f214aedeb1cfb4b53e96f34daeadf", name: "刘祥宇" },
                { uuid: "4e7d3957eb03468089ee5a0158b65c23", name: "周重天" },
                { uuid: "3c1e54c9f89b4b44d3b99aeac30e3a98", name: "吴雨桁" },
                { uuid: "cc3a23dbf9a243220193bd2fbe91bbfc", name: "陈达" },
                { uuid: "2cffa20a0d5660afe1702125c6f99b64", name: "杨峥芃" },
                { uuid: "23e449584dbb4c9f1e553e4784989b36", name: "董晓峰" },
                { uuid: "b967ef3c53695dd3b2edfd575f36716c", name: "庞天傲" },
                { uuid: "26140ab161208d644798e74810f0c011", name: "胡钧耀" },
            ];
            
            employeeList.forEach(emp => {
                const stats = employeePostCounts[emp.uuid] || { count: 0 };
                const countClass = stats.count === 0 ? 'zero' : '';
                // 取名字首字作为头像
                const avatarChar = emp.name.charAt(0);
                statsHtml += `
                    <div class="employee-stat-item">
                        <div class="avatar">${avatarChar}</div>
                        <div class="info">
                            <div class="name">${emp.name}</div>
                            <div class="count ${countClass}">${stats.count}</div>
                        </div>
                    </div>
                `;
            });
            
            employeeStatsContent.innerHTML = statsHtml;
        }
        
        // 渲染表格
        function renderTable(data) {
            const container = document.getElementById('tableContainer');
            if (!container) return;
            
            // 清空容器
            container.innerHTML = '';
            
            if (!data || data.length === 0) {
                container.innerHTML = '<div class="alert alert-info">暂无数据</div>';
                return;
            }
            
            // 创建表格
            const table = document.createElement('table');
            table.className = 'table table-hover';
            
            // 表头
            const thead = document.createElement('thead');
            thead.className = 'table-light';
            thead.innerHTML = `
                <tr>
                    <th style="width: 5%;">序号</th>
                    <th style="width: 10%;">发布者</th>
                    <th style="width: 10%;">UUID</th>
                    <th style="width: 15%;">标题</th>
                    <th style="width: 10%;">发布时间</th>
                    <th style="width: 35%;">内容</th>
                    <th style="width: 15%;">图片</th>
                </tr>
            `;
            table.appendChild(thead);
            
            // 表体
            const tbody = document.createElement('tbody');
            const results = data || [];
            
            for (let i = 0; i < results.length; i++) {
                const item = results[i];
                
                // 创建行
                const row = document.createElement('tr');
                
                // 序号列
                const indexCell = document.createElement('td');
                indexCell.textContent = item.index || '';
                row.appendChild(indexCell);
                
                // 发布者列
                const authorCell = document.createElement('td');
                authorCell.textContent = item.realname || '';
                row.appendChild(authorCell);
                
                // UUID列
                const uuidCell = document.createElement('td');
                const uuid = item.uuid || '';
                const displayUuid = uuid.length > 6 ? uuid.substring(0, 3) + '...' + uuid.slice(-3) : uuid;
                uuidCell.innerHTML = `<code title="${escapeHtml(uuid)}">${escapeHtml(displayUuid)}</code>`;
                row.appendChild(uuidCell);
                
                // 标题列
                const titleCell = document.createElement('td');
                titleCell.className = 'title-cell';
                titleCell.textContent = item.title || '无标题';
                row.appendChild(titleCell);
                
                // 时间列
                const timeCell = document.createElement('td');
                timeCell.className = 'time-cell';
                timeCell.textContent = item.created_at || '';
                row.appendChild(timeCell);
                
                // 内容列
                const contentCol = document.createElement('td');
                contentCol.className = 'content-cell';
                
                // 使用安全方式处理内容，避免JavaScript语法错误
                var content = (item.content || '');
                // 安全地存储内容到全局变量，直接使用原始数据
                allContents[item.index] = content; // 存储完整内容（已转义）
                var isLongContent = content.length > 50;
                var displayContent = isLongContent ? content.substring(0, 50) + '...' : content;
                var contentId = 'content-' + item.index;
                
                const contentSpan = document.createElement('span');
                contentSpan.id = contentId;
                contentSpan.className = isLongContent ? 'content-text truncated' : 'content-text';
                
                // 安全处理换行符：先按行分割内容，然后逐个添加文本节点和<br>元素
                const lines = displayContent.split('\n');
                lines.forEach((line, index) => {
                    if (index > 0) {
                        // 在每行之间添加换行
                        contentSpan.appendChild(document.createElement('br'));
                    }
                    // 添加文本内容
                    contentSpan.appendChild(document.createTextNode(line));
                });
                
                contentCol.appendChild(contentSpan);
                
                // 如果内容较长，添加展开按钮
                if (isLongContent) {
                    const expandBtn = document.createElement('button');
                    expandBtn.className = 'btn btn-link btn-sm p-0 ms-1 text-primary text-decoration-none';
                    expandBtn.type = 'button';
                    expandBtn.innerHTML = '<i class="bi bi-chevron-down"></i> <span class="btn-text">展开</span>';
                    expandBtn.onclick = () => toggleContent(item.index);
                    contentCol.appendChild(expandBtn);
                }
                
                row.appendChild(contentCol);
                
                // 图片列
                const imgCell = document.createElement('td');
                try {
                    const imgUrls = JSON.parse(item.img_url || '[]');
                    if (Array.isArray(imgUrls) && imgUrls.length > 0) {
                        const imgBaseUrl = 'https://image.reduct.cn';
                        imgUrls.forEach(url => {
                            const imgThumb = document.createElement('img');
                            imgThumb.src = imgBaseUrl + url;
                            imgThumb.style.width = '40px';
                            imgThumb.style.height = '40px';
                            imgThumb.style.objectFit = 'cover';
                            imgThumb.style.margin = '0 2px';
                            imgThumb.style.cursor = 'pointer';
                            imgThumb.onclick = () => showImg(imgBaseUrl + url);
                            imgThumb.title = '点击查看大图';
                            imgCell.appendChild(imgThumb);
                        });
                    } else {
                        imgCell.textContent = '无';
                    }
                } catch (e) {
                    imgCell.textContent = '解析错误';
                }
                
                row.appendChild(imgCell);
                
                tbody.appendChild(row);
            }
            
            table.appendChild(tbody);
            container.appendChild(table);
        }
        
        function showImg(url) {
            document.getElementById('modalImg').src = url;
            new bootstrap.Modal(document.getElementById('imgModal')).show();
        }
        
        // 存储所有帖子内容
        var allContents = {};
        
        function toggleContent(index) {
            var contentId = 'content-' + index;
            var contentSpan = document.getElementById(contentId);
            var fullContent = allContents[index]; // 直接使用已转义的内容
            var isExpanded = contentSpan.classList.contains('expanded');
            
            if (isExpanded) {
                // 收起内容
                contentSpan.classList.remove('expanded');
                contentSpan.classList.add('truncated');
                contentSpan.textContent = fullContent.substring(0, 50) + '...';
                const btn = contentSpan.nextElementSibling;
                btn.querySelector('.btn-text').textContent = '展开';
                btn.querySelector('i').className = 'bi bi-chevron-down';
            } else {
                // 展开内容
                contentSpan.classList.remove('truncated');
                contentSpan.classList.add('expanded');
                
                // 清空当前内容并重新构建
                contentSpan.innerHTML = '';
                const lines = fullContent.split('\n');
                lines.forEach((line, idx) => {
                    if (idx > 0) {
                        contentSpan.appendChild(document.createElement('br'));
                    }
                    contentSpan.appendChild(document.createTextNode(line));
                });
                
                const btn = contentSpan.nextElementSibling;
                btn.querySelector('.btn-text').textContent = '收起';
                btn.querySelector('i').className = 'bi bi-chevron-up';
            }
        }

        // HTML转义函数，用于防止XSS
        function escapeHtml(text) {
            if (typeof text !== 'string') {
                text = String(text);
            }
            var map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#x27;',
                '/': '&#x2F;'
            };
            return text.replace(/[&<>"'\/]/g, function(s) {
                return map[s];
            });
        }
    </script>
</body>
</html>
    """


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 减论科技员工发帖详情服务启动中...")
    print("=" * 60)
    print("📍 访问地址: http://localhost:5000")
    print("📡 API地址: http://localhost:5000/api/query")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
