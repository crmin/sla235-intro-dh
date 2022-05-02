from pprint import pprint

toc = """- 1. Life and Works
	- 1.1 Life
	- 1.2 Works
- 2. Metaphysics
- 3. Logic
- 4. Philosophy of Language
- 5. Philosophy of Mind
- 6. Ethics
- 7. Theology
- Bibliography
	- Primary texts in Latin
	- Primary texts in English translation
	- Selected Secondary Literature in English
- Academic Tools
- Other Internet Resources
- Related Entries"""

def split_toc_lines(toc_content):
    return toc_content.replace('\n-', '\n\n-').split('\n\n')

def split_toc_depth(toc_lines):
    toc_depths = toc_lines.split('\n')
    current_depth = toc_depths[0]
    next_depths = []
    for next_depth in toc_depths[1:]:
        next_depths.append(next_depth[1:])
    return current_depth, '\n'.join(next_depths)

def parse_toc(toc_content):
    if toc_content.strip() == '':
        return []

    toc_list = []
    for toc_lines in split_toc_lines(toc_content):
        current_depth, next_depths = split_toc_depth(toc_lines)
        toc_list.append({
            'content': current_depth,
            'subcontent': parse_toc(next_depths),
        })
    return toc_list

if __name__ == '__main__':
    pprint(parse_toc(toc), depth=4)