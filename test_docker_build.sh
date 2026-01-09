#!/bin/bash
echo "🧪 测试Docker构建..."

# 检查文件
echo "1. 检查必需文件..."
[ -f Dockerfile ] && echo "✅ Dockerfile" || echo "❌ Dockerfile"
[ -f requirements.txt ] && echo "✅ requirements.txt" || echo "❌ requirements.txt"
[ -f app.py ] && echo "✅ app.py" || echo "❌ app.py"
[ -f render.yaml ] && echo "✅ render.yaml" || echo "❌ render.yaml"

echo -e "\n2. 检查Dockerfile内容..."
cat Dockerfile | head -20

echo -e "\n3. 模拟Docker构建命令..."
echo "docker build -t tesla-dashboard ."
echo "docker run -p 8050:8050 tesla-dashboard"

echo -e "\n4. 检查应用结构..."
python -c "
try:
    from app import app
    print('✅ app.py 可以导入')
    if hasattr(app, 'server'):
        print('✅ app有server属性')
    else:
        print('❌ app缺少server属性')
except Exception as e:
    print(f'❌ app.py导入失败: {e}')
"

echo -e "\n🚀 Docker配置完成！提交后Render将使用Docker构建。"
