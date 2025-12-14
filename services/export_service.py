"""
Chat Export Service
Export conversations to Markdown and PDF formats.
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger("NexusAI.ExportService")


class ChatExporter:
    """Export chat conversations to various formats."""
    
    def __init__(self, app_name: str = "NexusAI"):
        self.app_name = app_name
    
    def to_markdown(
        self, 
        messages: List[Dict], 
        title: str = None,
        include_metadata: bool = True
    ) -> str:
        """
        Export messages to Markdown format.
        
        Args:
            messages: List of {"role": str, "content": str} dicts
            title: Optional title for the export
            include_metadata: Whether to include export metadata
        
        Returns:
            Markdown string
        """
        if not messages:
            return "# Empty Conversation\n\nNo messages to export."
        
        lines = []
        
        # Header
        chat_title = title or self._generate_title(messages)
        lines.append(f"# {chat_title}\n")
        
        if include_metadata:
            lines.append(f"*Exported from {self.app_name} on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
            lines.append("---\n")
        
        # Messages
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "user":
                lines.append(f"## 👤 You\n\n{content}\n")
            elif role == "assistant":
                lines.append(f"## ✨ {self.app_name}\n\n{content}\n")
            elif role == "system":
                lines.append(f"## ⚙️ System\n\n{content}\n")
            
            lines.append("---\n")
        
        return "\n".join(lines)
    
    def to_html(
        self, 
        messages: List[Dict], 
        title: str = None,
        dark_mode: bool = True
    ) -> str:
        """
        Export messages to HTML format (for PDF conversion).
        
        Args:
            messages: List of {"role": str, "content": str} dicts
            title: Optional title for the export
            dark_mode: Use dark theme styling
        """
        if not messages:
            return "<html><body><h1>Empty Conversation</h1></body></html>"
        
        chat_title = title or self._generate_title(messages)
        
        # Styles
        bg_color = "#0a0a0b" if dark_mode else "#ffffff"
        text_color = "#f0f0f0" if dark_mode else "#1a1a1a"
        user_bg = "#3b82f6" if dark_mode else "#dbeafe"
        user_text = "#ffffff" if dark_mode else "#1e40af"
        assistant_bg = "rgba(99, 102, 241, 0.15)" if dark_mode else "#f3f4f6"
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{chat_title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        body {{
            font-family: 'Inter', sans-serif;
            background: {bg_color};
            color: {text_color};
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        
        h1 {{
            color: {text_color};
            border-bottom: 2px solid #6366f1;
            padding-bottom: 10px;
        }}
        
        .metadata {{
            color: #888;
            font-size: 0.9em;
            margin-bottom: 30px;
        }}
        
        .message {{
            margin: 20px 0;
            padding: 16px 20px;
            border-radius: 16px;
        }}
        
        .user {{
            background: {user_bg};
            color: {user_text};
            margin-left: 20%;
        }}
        
        .assistant {{
            background: {assistant_bg};
            margin-right: 20%;
        }}
        
        .role {{
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 0.9em;
        }}
        
        pre {{
            background: #1a1a1e;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
        }}
        
        code {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>{chat_title}</h1>
    <div class="metadata">Exported from {self.app_name} on {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
"""
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Convert markdown to basic HTML
            content_html = self._markdown_to_html(content)
            
            role_label = "👤 You" if role == "user" else f"✨ {self.app_name}"
            role_class = role
            
            html += f"""
    <div class="message {role_class}">
        <div class="role">{role_label}</div>
        <div class="content">{content_html}</div>
    </div>
"""
        
        html += """
</body>
</html>"""
        
        return html
    
    def to_json(self, messages: List[Dict], title: str = None) -> Dict:
        """Export messages to JSON format."""
        return {
            "title": title or self._generate_title(messages),
            "exported_at": datetime.now().isoformat(),
            "app": self.app_name,
            "message_count": len(messages),
            "messages": messages
        }
    
    def _generate_title(self, messages: List[Dict]) -> str:
        """Generate a title from the first user message."""
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")[:50]
                # Clean up the content for title
                content = re.sub(r'[^\w\s-]', '', content).strip()
                if content:
                    return content + ("..." if len(msg.get("content", "")) > 50 else "")
        return "Untitled Conversation"
    
    def _markdown_to_html(self, text: str) -> str:
        """Basic markdown to HTML conversion."""
        # Code blocks
        text = re.sub(
            r'```(\w+)?\n(.*?)```',
            r'<pre><code>\2</code></pre>',
            text,
            flags=re.DOTALL
        )
        
        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Line breaks
        text = text.replace('\n\n', '</p><p>').replace('\n', '<br>')
        text = f'<p>{text}</p>'
        
        return text
    
    def save_markdown(self, messages: List[Dict], filepath: str, **kwargs) -> str:
        """Save messages as Markdown file."""
        content = self.to_markdown(messages, **kwargs)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    
    def save_html(self, messages: List[Dict], filepath: str, **kwargs) -> str:
        """Save messages as HTML file."""
        content = self.to_html(messages, **kwargs)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath


# Singleton instance
_exporter = None

def get_exporter() -> ChatExporter:
    """Get the chat exporter singleton."""
    global _exporter
    if _exporter is None:
        _exporter = ChatExporter()
    return _exporter
