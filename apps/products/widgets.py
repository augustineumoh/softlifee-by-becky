from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe


class CloudinaryVideoWidget(forms.TextInput):
    """
    Renders a text input for a video URL plus an "Upload Video" button that
    opens Cloudinary's JS Upload Widget. The file goes directly from the
    browser to Cloudinary — nothing passes through the Django/Railway server.
    """

    def render(self, name, value, attrs=None, renderer=None):
        cloud_name    = settings.CLOUDINARY_STORAGE['CLOUD_NAME']
        upload_preset = getattr(settings, 'CLOUDINARY_UPLOAD_PRESET', '')
        final_attrs   = self.build_attrs(self.attrs, attrs or {})
        widget_id     = final_attrs.get('id', f'id_{name}')
        button_id     = f'cld_btn_{widget_id}'
        status_id     = f'cld_status_{widget_id}'

        text_input = super().render(name, value, attrs, renderer)

        html = f"""
        {text_input}
        <button type="button" id="{button_id}" class="button" style="margin-left:8px;">
            &#8679; Upload from computer
        </button>
        <span id="{status_id}" style="margin-left:8px;color:green;font-weight:bold;"></span>
        <script>
        (function() {{
            if (!window._cldWidgetScriptAdded) {{
                window._cldWidgetScriptAdded = true;
                var s = document.createElement('script');
                s.src = 'https://upload-widget.cloudinary.com/global/all.js';
                document.head.appendChild(s);
            }}
            function _initCldBtn_{widget_id.replace('-', '_')}() {{
                var btn = document.getElementById('{button_id}');
                if (!btn) return;
                btn.addEventListener('click', function() {{
                    cloudinary.openUploadWidget({{
                        cloudName:    '{cloud_name}',
                        uploadPreset: '{upload_preset}',
                        sources:      ['local'],
                        resourceType: 'video',
                        multiple:     false,
                    }}, function(error, result) {{
                        if (!error && result && result.event === 'success') {{
                            document.getElementById('{widget_id}').value = result.info.secure_url;
                            document.getElementById('{status_id}').textContent = '✓ Uploaded!';
                        }}
                    }});
                }});
            }}
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', _initCldBtn_{widget_id.replace('-', '_')});
            }} else {{
                _initCldBtn_{widget_id.replace('-', '_')}();
            }}
        }})();
        </script>
        """
        return mark_safe(html)
