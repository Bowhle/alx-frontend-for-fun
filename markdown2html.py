#!/usr/bin/python3
'''
A script that codes markdown to HTML.

It takes two command-line arguments: the input Markdown file
and the output HTML file. It parses a subset of Markdown syntax
to generate basic HTML.
'''
import sys
import os
import re
import hashlib

def markdown_to_html(markdown_text):
    """Converts a list of markdown lines to HTML.

    Parses headings, unordered lists, ordered lists, bold, emphasis,
    and special commands to generate corresponding HTML.

    Args:
        markdown_text (list): A list of strings, where each string
                             represents a line of Markdown text.

    Returns:
        str: A string containing the generated HTML.
    """
    html_lines = []
    in_unordered_list = False
    in_ordered_list = False

    for line in markdown_text:
        line = line.rstrip()  # Remove trailing whitespace

        # Headings
        heading_match = re.match(r'^(#+) (.*)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            html_lines.append(f'<h{level}>{text}</h{level}>\n')
            continue

        # Unordered lists
        elif line.startswith('- '):
            if not in_unordered_list:
                html_lines.append('<ul>\n')
                in_unordered_list = True
            html_lines.append(f'<li>{format_text(line[2:])}</li>\n')
            continue
        elif in_unordered_list and not line.startswith('- '):
            html_lines.append('</ul>\n')
            in_unordered_list = False

        # Ordered lists
        elif line.startswith('* '):
            if not in_ordered_list:
                html_lines.append('<ol>\n')
                in_ordered_list = True
            html_lines.append(f'<li>{format_text(line[2:])}</li>\n')
            continue
        elif in_ordered_list and not line.startswith('* '):
            html_lines.append('</ol>\n')
            in_ordered_list = False

        # Special commands
        elif line.startswith('[['):
            command_match = re.match(r'\[\[(.*?)\]\]', line)
            if command_match:
                content = command_match.group(1)
                md5_hash = hashlib.md5(content.encode()).hexdigest()
                html_lines.append(f'<p>{md5_hash}</p>\n')
                continue

        elif line.startswith('(('):
            command_match = re.match(r'\(\((.*?)\)\)', line)
            if command_match:
                content = command_match.group(1).lower().replace('c', '').replace('C', '')
                html_lines.append(f'<p>{content}</p>\n')
                continue

        # Simple text paragraphs
        elif line.strip():
            formatted_line = format_text(line)
            if html_lines and html_lines[-1].startswith('<p>'):
                html_lines[-1] = html_lines[-1][:-3] + '<br/>\n' + formatted_line + '</p>\n'
            else:
                html_lines.append(f'<p>\n{formatted_line}\n</p>\n')
        elif html_lines and html_lines[-1].startswith('<p>'):
            html_lines[-1] = html_lines[-1][:-3] + '</p>\n'

    # Close any open lists at the end of the file
    if in_unordered_list:
        html_lines.append('</ul>\n')
    if in_ordered_list:
        html_lines.append('</ol>\n')

    return "".join(html_lines)

def format_text(text):
    """Formats text for bold and emphasis.

    Replaces Markdown bold and emphasis syntax with HTML tags.

    Args:
        text (str): The input string containing Markdown formatting.

    Returns:
        str: The string with HTML bold and emphasis tags.
    """
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.*?)__', r'<em>\1</em>', text)
    return text

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: ./markdown2html.py README.md README.html', file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(input_file):
        print(f'Missing {input_file}', file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_file, 'r', encoding='utf-8') as f_in:
            markdown_content = [line.rstrip('\n') for line in f_in.readlines()] # Remove trailing newlines too!
    except IOError:
        print(f'Error reading {input_file}', file=sys.stderr)
        sys.exit(1)

    html_output = markdown_to_html(markdown_content)

    try:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(html_output)
        sys.exit(0)
    except IOError:
        print(f'Error writing to {output_file}', file=sys.stderr)
        sys.exit(1)
