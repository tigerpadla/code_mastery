"""
Custom template filters for quiz display.
"""

import re
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


@register.filter(name='render_code')
def render_code(text):
    """
    Convert code tags to styled <code> elements.

    Handles:
    - [code]...[/code] tags for inline code
    - [codeblock]...[/codeblock] tags for multi-line code blocks
    - Triple backtick code blocks (```...```)
    - Literal \\n characters converted to line breaks
    - Backticks displayed as visible characters (for template literals)

    Usage: {{ question.text|render_code }}
    """
    if not text:
        return text

    # First escape HTML to prevent XSS
    text = escape(text)

    # Convert literal \n to actual newlines (AI sometimes sends these)
    text = text.replace('\\n', '\n')

    # Remove stray punctuation that AI sometimes adds after code blocks
    text = re.sub(r'\[/code\]\s*[?;:]\s*$', '[/code]', text)
    text = re.sub(r'\[/codeblock\]\s*[?;:]\s*$', '[/codeblock]', text)

    # Handle triple backtick code blocks (```...```)
    text = re.sub(
        r'```(?:\w+)?\n?(.*?)```',
        r'<pre><code class="code-block">\1</code></pre>',
        text,
        flags=re.DOTALL
    )

    # Handle [codeblock]...[/codeblock] tags for multi-line code
    # First, protect backticks inside codeblock by replacing with placeholder
    def protect_backticks_codeblock(match):
        content = match.group(1).replace('`', '&#96;')
        return f'<pre><code class="code-block">{content}</code></pre>'
    
    text = re.sub(
        r'\[codeblock\](.*?)\[/codeblock\]',
        protect_backticks_codeblock,
        text,
        flags=re.DOTALL
    )

    # Handle [code]...[/code] tags for inline code
    # Also protect backticks inside code tags
    def protect_backticks_code(match):
        content = match.group(1).replace('`', '&#96;')
        return f'<code class="code-inline">{content}</code>'
    
    text = re.sub(
        r'\[code\](.*?)\[/code\]',
        protect_backticks_code,
        text,
        flags=re.DOTALL
    )

    # Convert any remaining backticks to visible HTML entity (not code styling)
    # This ensures template literal backticks are visible
    text = text.replace('`', '&#96;')

    # Convert remaining newlines to <br> for display (outside of pre tags)
    # But preserve newlines inside <pre> tags
    parts = re.split(r'(<pre>.*?</pre>)', text, flags=re.DOTALL)
    result = []
    for part in parts:
        if part.startswith('<pre>'):
            result.append(part)
        else:
            result.append(part.replace('\n', '<br>'))
    text = ''.join(result)

    return mark_safe(text)
