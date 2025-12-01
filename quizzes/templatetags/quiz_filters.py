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
    Convert backtick-wrapped code to styled <code> tags.
    
    Handles both:
    - Inline code: `code here`
    - Multi-line code blocks: ```code here```
    
    Usage: {{ question.text|render_code }}
    """
    if not text:
        return text
    
    # First escape HTML to prevent XSS
    text = escape(text)
    
    # Handle multi-line code blocks (```) first
    # Replace ```...``` with <pre><code>...</code></pre>
    text = re.sub(
        r'```(\w*)\n?(.*?)```',
        r'<pre><code class="code-block">\2</code></pre>',
        text,
        flags=re.DOTALL
    )
    
    # Handle inline code (single backticks)
    # Replace `...` with <code>...</code>
    text = re.sub(
        r'`([^`]+)`',
        r'<code class="code-inline">\1</code>',
        text
    )
    
    return mark_safe(text)
