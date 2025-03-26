from ete3 import Tree, TreeStyle, NodeStyle, TextFace
import re
import tempfile
import os
import time


class MindmapGenerator:
    def __init__(self, default_output_folder="static/mindmaps"):
        """
        初始化思维导图生成器

        参数:
            default_output_folder: 默认输出文件夹路径
        """
        self.text = None
        self.default_output_folder = default_output_folder

        # 确保输出文件夹存在
        os.makedirs(self.default_output_folder, exist_ok=True)

    def parse_text_to_tree(self, text):
        """将文本解析为树形结构的newick格式字符串"""
        lines = text.strip().split('\n')

        # 提取标题作为根节点
        root_name = lines[0].lstrip('#').strip() if lines else "思维导图"

        # 构建节点层级结构
        nodes = {0: [root_name, []]}  # 格式: {level: [node_name, [children]]}
        current_level = 0

        for line in lines[1:]:
            if not line.strip():
                continue

            # 检测缩进或标题级别
            level = 0
            hash_match = re.match(r'^(#+)\s+(.+)$', line)
            dash_match = re.match(r'^(\s*)-\s+(.+)$', line)  # 匹配破折号形式的列表项

            if hash_match:
                level = len(hash_match.group(1))
                content = hash_match.group(2).strip()
            elif dash_match:
                # 破折号形式的列表项视为比当前层级深一级
                indentation = dash_match.group(1)
                base_level = indentation.count('\t') + indentation.count('    ')
                level = base_level + current_level + 1  # 比上一级多一级
                content = dash_match.group(2).strip()
            else:
                indent_match = re.match(r'^(\s*)(.+)$', line)
                if indent_match:
                    indentation = indent_match.group(1)
                    level = indentation.count('\t') + indentation.count('    ')
                    content = indent_match.group(2).strip()
                else:
                    content = line.strip()
                    level = current_level + 1

            # 限制层级增加（非破折号项）
            if not dash_match and level > current_level + 1:
                level = current_level + 1

            # 构建节点
            node = [content, []]

            # 查找父节点
            parent_level = level - 1
            while parent_level >= 0 and parent_level not in nodes:
                parent_level -= 1

            if parent_level >= 0:
                nodes[parent_level][1].append(node)

            nodes[level] = node
            current_level = level

            # 清除更深层级的节点
            for k in list(nodes.keys()):
                if k > level:
                    del nodes[k]

        # 转换为ETE Tree结构
        return self.build_tree_from_nodes(nodes[0])

    def build_tree_from_nodes(self, node):
        """从节点结构构建ETE Tree对象"""
        t = Tree(name=node[0])
        for child in node[1]:
            t.add_child(self.build_tree_from_nodes(child))
        return t

    def generate_mind_map_png(self, text, output_file="mind_map.png"):
        """生成思维导图PNG图片"""
        # 解析文本为树结构
        tree = self.parse_text_to_tree(text)

        # 自定义树样式
        ts = TreeStyle()
        ts.show_leaf_name = False
        ts.show_scale = False
        ts.branch_vertical_margin = 15  # 垂直间距
        ts.rotation = 90  # 水平布局
        ts.show_border = False

        # 设置节点样式和标签
        def layout(node):
            # 为不同层级设置不同样式
            ns = NodeStyle()
            ns["shape"] = "sphere"

            if node.is_root():
                ns["size"] = 15
                ns["fgcolor"] = "#3498db"  # 蓝色
                face = TextFace(node.name, fgcolor="black", fsize=14, bold=True)
            elif not node.is_leaf():
                ns["size"] = 10
                ns["fgcolor"] = "#2ecc71"  # 绿色
                face = TextFace(node.name, fgcolor="black", fsize=12)
            else:
                ns["size"] = 8
                ns["fgcolor"] = "#e74c3c"  # 红色
                face = TextFace(node.name, fgcolor="black", fsize=10)

            node.set_style(ns)
            face.margin_left = 5
            face.margin_right = 5
            node.add_face(face, column=0, position="branch-right")

        ts.layout_fn = layout

        # 导出为PNG图片
        tree.render(output_file, tree_style=ts, dpi=300)
        print(f"思维导图已保存为: {output_file}")
        return output_file

    def generate(self, sample_text: str = "", output_path=None):
        """
        生成思维导图

        参数:
            sample_text: 输入文本
            output_path: 指定输出文件路径，如不指定则使用默认路径

        返回:
            生成的思维导图文件路径
        """
        user_input = sample_text
        print(f"输入文本为:{user_input}")

        # 如果没有提供输出路径，则创建一个默认路径
        if not output_path:
            timestamp = int(time.time())
            output_filename = f"mindmap_{timestamp}.png"
            output_path = os.path.join(self.default_output_folder, output_filename)

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 生成思维导图PNG
        return self.generate_mind_map_png(user_input, output_path)