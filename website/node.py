import re

FULL_PATH_DELIMITER = '/'
ROOT_PATH = ''
LINK_SYMBOL = '>'
MAX_DEPTH = 100

class Node:
    def __init__(self, text, link):
        self.text = text
        self.link = link
        self.parent = None
        self.children = []

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def __eq__(self, other):
        return self.text == other.text

    def set_default_full_path(self):
        """
            需在确立父节点后才能获取full_path
            full_path不包含ROOT
        """
        node_ptr = self
        full_path = []
        while node_ptr.text != 'ROOT':
            full_path.append(node_ptr.text)
            node_ptr = node_ptr.parent
        return FULL_PATH_DELIMITER.join(full_path[::-1])

    @property
    def full_link_path(self):
        node_ptr = self
        full_path = []
        while node_ptr.text != 'ROOT':
            if node_ptr.link:
                full_path.append(node_ptr.text)
            node_ptr = node_ptr.parent
        return ' '.join(full_path[::-1])

    def save_to_txt(self, path):
        with open(path, 'w', encoding='utf8') as fp:
            fp.write(self.to_txt_string(recursion=True))

    def to_txt_string(self, level=0, *, recursion):
        islink = LINK_SYMBOL if self.link else ''
        string = '\t' * level + self.text + ' ' + islink + '\n\n'
        if level == 0 or recursion or not self.link:
            for child in self.children:
                string += child.to_txt_string(level + 1, recursion=recursion)
        return string

    def strict_search(self, query):
        keywords = query.split()

        results = []
        last_result = None
        for link_node in self.all_sub_link_nodes(max_depth=MAX_DEPTH): # 在所有link_node下搜索
            # matched_results = []
            for node in link_node.all_sub_page_nodes(): # 只搜索当前子导图
                if last_result and node.is_sub_node_of(last_result): # 排除匹配节点的子节点
                    continue

                if node.strict_match(keywords):
                    results.append(node)
                    last_result = node
        return results

    def strict_match(self, keywords):
        if keywords[-1] != self.text.lower():
            return False

        full_path = self.full_path.lower().split(FULL_PATH_DELIMITER) # 与节点内容匹配
        for keyword in keywords:
            if keyword not in full_path:
                return False

        return True

    def is_sub_node_of(self, parent):
        return self.full_path.startswith(parent.full_path)

    def vague_search(self, query):
        keywords = query.split()
        results = []
        for node in self.all_sub_nodes(max_depth=MAX_DEPTH):
            if node.vague_match(keywords):
                results.append(node)
        return results

    def vague_match(self, keywords):
        """
            可添加同义词搜索功能，暂未实现
        """
        if keywords[-1] not in self.text.lower():
            return False

        full_path = self.full_path.lower()  # 在节点内容中
        for keyword in keywords:
            if keyword not in full_path:
                return False

        return True

    def full_path_search(self, full_path):
        # 兄弟节点不能重名，否则full_path不唯一
        for node in self.all_sub_nodes(max_depth=MAX_DEPTH):
            if node.full_path == full_path:
                return node

    def all_sub_nodes(self, depth=0, *, max_depth):
        if depth > max_depth:
            return

        yield self
        for child in self.children:
            yield from child.all_sub_nodes(depth + 1, max_depth=max_depth)

    def all_sub_link_nodes(self, depth=0, *, max_depth):
        if depth > max_depth:
            return

        if self.link:
            yield self
        for child in self.children:
            if child.link:
                yield from child.all_sub_link_nodes(depth + 1, max_depth=max_depth)
            else:
                yield from child.all_sub_link_nodes(depth, max_depth=max_depth)

    def all_sub_page_nodes(self):
        yield self
        for child in self.children:
            if not child.link:
                yield from child.all_sub_page_nodes()

    def to_links(self, root, level=0, recursion=False, space='&nbsp', new_line='<br>'):
        link_string = '>' if self.link else ''

        line = self.text + ' ' + link_string
        front = self.get_front(root, space, new_line)
        # print(front + self.text)

        a_tag = """<a href="http://127.0.0.1:5000/search/?q={0}+-f">{1}</a>""".format(
            self.full_path,
            line)
        if self == root:
            links = front + a_tag +root.get_sub_1_links()
        else:
            links = front + a_tag +new_line

        if level == 0 or recursion or not self.link:
            for child in self.children:
                links += child.to_links(root, level + 1, recursion, space, new_line)

        return links

    def get_sub_1_links(self):
        string=''
        space='&nbsp'
        new_line = '<br>'

        for child in self.children:
            link_string = '>' if child.link else ''
            line = child.text + ' ' + link_string

            string += space*3 + """<a href="http://127.0.0.1:5000/search/?q={0}+-f">{1}</a>""".format(
            child.full_path,
            line)

        return string + new_line

    def get_front(self, root, space, new_line):
        """
            不好用语言描述算法，功能是打印树形结构
        """
        if self.full_path==root.full_path:
            return space*10

        times = 8 # 间隔
        l = []
        node_ptr = self.parent
        while node_ptr.parent:
            if  node_ptr.full_path.startswith(root.full_path) and node_ptr.full_path!=root.full_path:
                l.append(node_ptr)
                node_ptr = node_ptr.parent
            else:
                break
        front = space*10
        l.reverse()
        print(self,l)
        for node in l:
            if node.parent.children.index(node) < len(node.parent.children) - 1:
                front += ' │' + space * times
            else:
                front += space * times
        front += ' │' + space * times + new_line+space*10
        for node in l:
            if node.parent.children.index(node) < len(node.parent.children) - 1:
                front += ' │' + space * times
            else:
                front += space * times
        return '<span>' + front + ' │' + '_' * (times ) + '</span>'

    def html_header(self):
        l = []
        node_ptr = self
        while node_ptr and node_ptr.text != "ROOT":
            l.append(node_ptr)
            node_ptr = node_ptr.parent

        space='&nbsp'
        html_header = space*10
        for node in l[::-1]:
            html_header += """<a href="http://127.0.0.1:5000/search/?q={0}+-f">{1}</a>""".format(
                node.full_path,
                node.text + "&nbsp" * 2) + "&nbsp" * 3

        return html_header + "<br>" * 2

    def update_links_from(self, original_node):
        """
            按照original_node中的link更新changed中的link
        """
        changed = self

        original_linked_nodes = original_node.all_sub_link_nodes(max_depth=1)
        changed_linked_nodes = changed.all_sub_link_nodes(max_depth=MAX_DEPTH)

        original_links_dict = {}

        for linked_node in original_linked_nodes:
            original_links_dict[linked_node.text] = linked_node

        for linked_node in changed_linked_nodes:
            if linked_node.text != changed.text and linked_node.text in original_links_dict:
                for child in original_links_dict[linked_node.text].children:
                    linked_node.children.append(child)


def load_txt(path):
    with open(path, encoding='utf8') as fp:
        note = fp.read()
        return to_tree(note)


def to_tree(note):
    last_level = -1
    root_node = Node('ROOT', False)
    last_node = root_node
    parent_node = root_node
    for line in note.split('\n'):
        if not line.strip():
            continue
        text, link, level = process_line(line)
        node = Node(text, link)
        if level > last_level + 1:
            raise Exception('缩进层次跳跃' + text)
        elif level == last_level + 1:
            parent_node = last_node
        else:
            for i in range(last_level - level):
                parent_node = parent_node.parent

        node.parent = parent_node
        parent_node.children.append(node)

        node.full_path = node.set_default_full_path()

        last_level = level
        last_node = node

    return root_node.children[0]


def process_line(line):
    line = line.rstrip()
    if line.endswith(LINK_SYMBOL):
        link = True
        line = line[:-1].rstrip()
    else:
        link = False
    line, level = re.subn('\t', '', line)

    if line.startswith(' '):
        raise Exception('缩进中含有空格' + line) # 混入空格将引起层次错乱
    return line, link, level


def search(query, *, mode):
    query = query.strip()
    root_node = load_txt(ROOT_PATH)
    if mode == 'strict':
        return root_node.strict_search(query.lower())
    elif mode == 'vague':
        return root_node.vague_search(query.lower())
    elif mode == 'full_path':
        return root_node.full_path_search(query)
    else:
        raise Exception('未定义搜索模式：' + mode)


def alter(changed):
    root_node = load_txt(ROOT_PATH)
    original_node = root_node.full_path_search(changed.full_path)

    changed.update_links_from(original_node)

    parent = original_node.parent
    pos = parent.children.index(original_node)
    parent.children[pos] = changed

    if changed.text == 'Note':
        return parent.children[0] # 如果是修改主页，new_root不再是root_node
    else:
        return root_node

def init():
    global ROOT_PATH
    d={}
    with open('Note.ini') as fp:
        for line in fp:
            key,value=line.split('=')
            d[key]=value
        ROOT_PATH=d['ROOT_PATH']
        ROOT_PATH=ROOT_PATH+'Note.txt'

init()

if __name__ == '__main__':
    root_node = load_txt(ROOT_PATH)

    # test for full_path search
    # result = search('Note/数学', mode='full_path')
    # result.save_to_txt('result.txt')

    # test for all_nodes
    # print(list(root_node.all_sub_nodes(max_depth=2)))
    # print(list(root_node.all_sub_link_nodes(max_depth=2)))
    # print(list(root_node.all_sub_page_nodes()))

    # test for strict search
    # results = search('Note 数学', mode='strict')
    # for result in results:
    #     print(result.full_path)

    # test for vague search
    # results = search('1', mode='vague')
    # for result in results:
    #     print(result.full_path)

    # test for alter
    # changed = load_txt('Note1.txt')
    # changed.full_path='Note'
    # new_root = alter(changed)
    # print(new_root.to_txt_string())

    # root_node=load_txt(ROOT_PATH)
    # print(root_node.to_links(root_node,space=' ',new_line='\n'))