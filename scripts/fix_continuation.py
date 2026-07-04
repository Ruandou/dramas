#!/usr/bin/env python3
"""修复剧本中的空管子续行——将多句对白合并到同一格。"""
import argparse, os, re, sys

def fix_continuation(fpath: str) -> int:
    with open(fpath) as f:
        lines = f.readlines()
    
    new_lines = []
    prev_row = None  # (index in new_lines, content) of last table row with content
    skip_next = False
    fixed = 0
    
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')
        
        # Check if this is a table row
        is_table = stripped.strip().startswith('|') and stripped.strip().endswith('|')
        
        if not is_table:
            new_lines.append(line)
            prev_row = None
            continue
        
        # Split by pipe
        cells = stripped.split('|')
        # cells[0] is empty (before first |), cells[1] is first column
        first_cell = cells[1].strip() if len(cells) > 1 else ''
        
        if first_cell and len(cells) >= 12:
            # This is a normal table row with content in first cell (镜号)
            new_lines.append(line)
            prev_row = len(new_lines) - 1
        elif not first_cell and prev_row is not None and len(cells) >= 12:
            # This is a continuation row — merge into previous row
            last_cell_content = cells[-2].strip()  # content in last cell (cells[-1] is trailing empty)
            if last_cell_content:
                # Get previous row and append the continuation content
                prev_line = new_lines[prev_row].rstrip('\n').rstrip('\r\n')
                # Insert the continuation content before the closing |
                prev_line = prev_line.rstrip('|')
                prev_line = prev_line + last_cell_content + '|\n'
                new_lines[prev_row] = prev_line
                fixed += 1
            # Skip this continuation row
        else:
            new_lines.append(line)
            prev_row = None
    
    if fixed > 0:
        with open(fpath, 'w') as f:
            f.writelines(new_lines)
    
    return fixed


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ep', required=True)
    p.add_argument('--project-root', required=True)
    a = p.parse_args()
    
    fpath = os.path.join(a.project_root, "剧本", a.ep, f"{a.ep}_剧本.md")
    if not os.path.exists(fpath):
        print(f"文件不存在: {fpath}"); sys.exit(1)
    
    n = fix_continuation(fpath)
    print(f"{a.ep}: 合并 {n} 行续行")


if __name__ == "__main__":
    main()
