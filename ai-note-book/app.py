from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
import os
import asyncio
import time
import json
import base64
from datetime import datetime

# 导入数据库实例
from models import db
# 导入Note模型
from models.Note import Note

# 如果使用单独的数据库配置文件
from config.db_config import get_db_uri

from config.APIconfig import APIConfig
from utils.openai_handler import AIHandler
from utils.prompts import get_prompts
from utils.mindmap_generator import MindmapGenerator

# 创建Flask应用
app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()  # 使用配置函数

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化应用
db.init_app(app)

# 用于保存生成的思维导图图像
UPLOAD_FOLDER = 'static/mindmaps'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化AI配置
load_dotenv(verbose=True)
config = APIConfig()
env_key = "DEEPSEEK_API_KEY"
default_api_key = os.getenv(env_key, "")
deepseek_config = APIConfig.get_config(provider="deepseek")
default_api_base = os.getenv("DEEPSEEK_API_KEY_API_BASE", deepseek_config["api_base"])
mindmap_generator = MindmapGenerator(default_output_folder="static/mindmaps")

# 创建全局处理器实例
ai_handler = AIHandler(
    api_key=default_api_key,
    api_base=default_api_base,
    provider="deepseek"
)
mindmap_generator = MindmapGenerator()
prompts = get_prompts()


# 异步运行函数
def run_async(coro):
    return asyncio.run(coro)


# 笔记相关路由
@app.route('/api/notes', methods=['GET'])
def get_notes():
    """获取用户所有笔记"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': 'Missing user_id parameter'}), 400

        notes = Note.query.filter_by(user_id=user_id).order_by(Note.update_time.desc()).all()
        return jsonify({
            'success': True,
            'notes': [note.to_dict() for note in notes]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """获取笔记详情"""
    try:
        note = Note.query.get(note_id)
        if not note:
            return jsonify({'error': 'Note not found'}), 404

        return jsonify({
            'success': True,
            'note': note.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_notes_by_user(user_id):
    """获取用户的所有笔记"""
    try:
        # 查询该用户的所有笔记
        notes = Note.query.filter_by(user_id=user_id).all()

        if not notes:
            return jsonify({'error': 'No notes found for this user'}), 404

        # 将所有笔记转换为字典格式
        notes_list = [note.to_dict() for note in notes]

        return jsonify({
            'success': True,
            'notes': notes_list
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/notes', methods=['POST'])
def create_note():
    """创建新笔记"""
    try:
        data = request.get_json()

        # 检查必填字段
        required_fields = ['user_id', 'title', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing {field} parameter'}), 400

        # 创建笔记实例
        note = Note(
            user_id=data['user_id'],
            title=data['title'],
            content=data['content'],
            image=data.get('image', '')
        )

        # 保存到数据库
        db.session.add(note)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Note created successfully',
            'note': note.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """更新笔记"""
    try:
        note = Note.query.get(note_id)
        if not note:
            return jsonify({'error': 'Note not found'}), 404

        data = request.get_json()

        # 更新笔记字段
        if 'title' in data:
            note.title = data['title']
        if 'content' in data:
            note.content = data['content']
        if 'image' in data:
            note.image = data['image']

        # 保存更新
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Note updated successfully',
            'note': note.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """删除笔记"""
    try:
        note = Note.query.get(note_id)
        if not note:
            return jsonify({'error': 'Note not found'}), 404

        db.session.delete(note)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Note deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/generate-mindmap', methods=['POST'])
def generate_mindmap():
    """接收文本并生成思维导图，并选择性保存为笔记"""
    start_time = time.time()

    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text parameter'}), 400

        text = data['text']
        user_id = data.get('user_id')
        save_as_note = data.get('save_as_note', False)

        # 处理文本并生成思维导图
        result = run_async(ai_handler.process_text(text, prompts["prompt"]))

        # 生成思维导图，确保函数返回路径
        timestamp = int(time.time())
        filename = f"mindmap_{user_id if user_id else 'anonymous'}_{timestamp}.png"
        output_path = os.path.join(UPLOAD_FOLDER, filename)

        # 调用MindmapGenerator生成图片
        try:
            # 假设generate方法会把图片保存到output_path
            mindmap_path = mindmap_generator.generate(result, output_path)
            if not mindmap_path:
                mindmap_path = output_path  # 如果返回None，使用我们指定的路径
        except Exception as e:
            return jsonify({'success': False, 'error': f"Failed to generate mindmap: {str(e)}"}), 500

        # 检查文件是否存在
        if not os.path.exists(mindmap_path):
            return jsonify({
                'success': False,
                'error': f"Mindmap file not found at {mindmap_path}"
            }), 500

        # 将图像转换为base64
        with open(mindmap_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')

        # 如果请求要求保存为笔记且提供了用户ID
        note_id = None
        if save_as_note and user_id:
            title = data.get('title', f"思维导图笔记 {datetime.now().strftime('%Y-%m-%d %H:%M')}")

            # 创建新笔记
            note = Note(
                user_id=user_id,
                title=title,
                content=result,  # 处理后的文本作为内容
                image=mindmap_path  # 保存图片路径
            )

            db.session.add(note)
            db.session.commit()
            note_id = note.id

        end_time = time.time()

        response_data = {
            'success': True,
            'processed_text': result,
            'mindmap_image': img_data,
            'mindmap_path': mindmap_path,
            'processing_time': end_time - start_time
        }

        if note_id:
            response_data['note_id'] = note_id
            response_data['message'] = 'Note saved successfully'

        return jsonify(response_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 测试数据库连接
        db.session.execute('SELECT 1')
        return jsonify({'status': 'ok', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'error', 'database': 'disconnected', 'error': str(e)}), 500


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # 命令行模式 - 为了兼容原有功能
        with app.app_context():
            db.create_all()  # 确保表已创建
            class Notebook:
                def __init__(self):
                    self.config = config
                    self.default_api_key = default_api_key
                    self.default_api_base = default_api_base

                async def process(self):
                    chunks = "李彦宏是中国著名的互联网企业家，他于1968年11月17日出生于山西省阳泉市。2000年，李彦宏创立了百度公司，这是一家全球领先的搜索引擎公司。百度公司的总部位于北京市。2021年，李彦宏正式卸任百度公司的职务。"

                    result = await ai_handler.process_text(chunks, prompts["prompt"])
                    print(f"结果总结：{result}")

                    print(f"开始生成思维导图")
                    mindmap_generator.generate(result)

            start_time = time.time()
            notebook = Notebook()
            asyncio.run(notebook.process())
            end_time = time.time()
            print(f"方法调用耗时为：{end_time-start_time}s")

    else:
        app.run(host='0.0.0.0', port=5000, debug=True)