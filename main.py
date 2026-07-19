"""
Musnad Line Converter - Kivy Application
Converts Arabic text to the Musnad script and saves it as images.
Each image contains up to 320 characters, with sequential numbering.
Images are saved in the download/ms folder on external storage.
"""
import os
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from kivy.utils import platform
from kivy.logger import Logger

# Libraries for images and files
from PIL import Image as PILImage, ImageDraw, ImageFont
import os
import zipfile
import io

# For Android storage access
try:
    from android.permissions import request_permissions, Permission
    HAS_ANDROID_PERMS = True
except ImportError:
    HAS_ANDROID_PERMS = False
    Permission = None
    request_permissions = None

# Register the Musnad font - wrap in try/except to prevent crashes
try:
    resource_add_path(os.path.dirname(os.path.abspath(__file__)))
    LabelBase.register(name='Musnad', fn_regular='ms.ttf')
except Exception as e:
    Logger.warning(f'Font registration warning: {str(e)}')

class MusnadConverterApp(App):
    def build(self):
        self.title = 'Musnad Line Converter'
        self.root = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # App state
        self.text_input = None
        self.output_label = None
        self.char_count_label = None
        self.status_label = None
        self.download_btn = None

        # Build UI
        self.build_ui()

        # Request permissions if on Android - only if module is available
        if platform == 'android' and HAS_ANDROID_PERMS:
            self.request_permissions()

        return self.root

    def build_ui(self):
        # Header
        header = BoxLayout(size_hint_y=None, height=60, spacing=10)
        header.add_widget(Label(text='Musnad Line Converter', font_size='24sp', bold=True, color=(0.2, 0.2, 0.2, 1)))
        self.root.add_widget(header)

        # Input field (normal font)
        input_box = BoxLayout(orientation='vertical', size_hint_y=None, height=150)
        input_box.add_widget(Label(text='Enter Arabic text (normal font)', size_hint_y=None, height=30, halign='right'))
        self.text_input = TextInput(text='', multiline=True, font_size='18sp', size_hint_y=None, height=120,
                                    background_color=(1, 1, 1, 0.9), foreground_color=(0, 0, 0, 1),
                                    halign='right', valign='top')
        input_box.add_widget(self.text_input)
        self.root.add_widget(input_box)

        # Character counter
        self.char_count_label = Label(text='0 chars', size_hint_y=None, height=30, color=(0.4, 0.3, 0.2, 1))
        self.root.add_widget(self.char_count_label)

        # Control buttons
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        convert_btn = Button(text='Convert', background_color=(0.4, 0.3, 0.2, 1), color=(1, 1, 1, 1))
        convert_btn.bind(on_press=self.convert_text)
        clear_btn = Button(text='Clear', background_color=(0.7, 0.6, 0.5, 1))
        clear_btn.bind(on_press=self.clear_text)
        example_btn = Button(text='Example', background_color=(0.7, 0.6, 0.5, 1))
        example_btn.bind(on_press=self.load_example)
        test_btn = Button(text='Test Font', background_color=(0.2, 0.6, 0.2, 1), color=(1, 1, 1, 1))
        test_btn.bind(on_press=self.test_font)
        btn_layout.add_widget(convert_btn)
        btn_layout.add_widget(clear_btn)
        btn_layout.add_widget(example_btn)
        btn_layout.add_widget(test_btn)
        self.root.add_widget(btn_layout)

        # Output area showing text in Musnad font
        output_box = BoxLayout(orientation='vertical', size_hint_y=None, height=200)
        output_box.add_widget(Label(text='Text in Musnad Script', size_hint_y=None, height=30, halign='right'))
        scroll = ScrollView(size_hint_y=None, height=170)
        self.output_label = Label(text='Enter text and press Convert', font_size='28sp', font_name='Musnad',
                                  color=(0.1, 0.1, 0.1, 1), halign='right', valign='top',
                                  text_size=(self.root.width - 40, None))
        scroll.add_widget(self.output_label)
        output_box.add_widget(scroll)
        self.root.add_widget(output_box)

        # Download images button
        self.download_btn = Button(text='Download Images', size_hint_y=None, height=50,
                                   background_color=(0.8, 0.4, 0, 1), color=(1, 1, 1, 1))
        self.download_btn.bind(on_press=self.download_images)
        self.root.add_widget(self.download_btn)

        # Status bar
        self.status_label = Label(text='Ready', size_hint_y=None, height=30, color=(0.4, 0.4, 0.4, 1))
        self.root.add_widget(self.status_label)

        # Bind text changes to update counter and live preview
        self.text_input.bind(text=self.on_text_change)

    def on_text_change(self, instance, value):
        # Update character counter
        self.char_count_label.text = '{} chars'.format(len(value))
        # Show text in Musnad font (live preview)
        if value.strip() == '':
            self.output_label.text = 'Enter text and press Convert'
        else:
            self.output_label.text = value

    def convert_text(self, instance):
        # Same as live preview, but can include additional processing
        text = self.text_input.text
        if text.strip() == '':
            self.output_label.text = 'Enter text and press Convert'
        else:
            self.output_label.text = text
        self.status_label.text = 'Converted'

    def clear_text(self, instance):
        self.text_input.text = ''
        self.output_label.text = 'Enter text and press Convert'
        self.char_count_label.text = '0 chars'
        self.status_label.text = 'Cleared'

    def load_example(self, instance):
        example = 'بسم الله الرحمن الرحيم\nالحمد لله رب العالمين'
        self.text_input.text = example
        self.output_label.text = example
        self.char_count_label.text = '{} chars'.format(len(example))
        self.status_label.text = 'Example loaded'

    def test_font(self, instance):
        test_str = 'المُسند خط عربي قديم'
        self.text_input.text = test_str
        self.output_label.text = test_str
        self.char_count_label.text = '{} chars'.format(len(test_str))
        self.status_label.text = 'Font test: working'

    def request_permissions(self):
        if not HAS_ANDROID_PERMS or not request_permissions:
            Logger.warning('Android permissions module not available')
            return
            
        try:
            perms = [Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]
            # On Android 11+ we may need MANAGE_EXTERNAL_STORAGE
            try:
                from android.permissions import Permission as Perm
                if hasattr(Perm, 'MANAGE_EXTERNAL_STORAGE'):
                    perms.append(Perm.MANAGE_EXTERNAL_STORAGE)
            except:
                pass
            request_permissions(perms)
        except Exception as e:
            Logger.error('Error requesting permissions: {}'.format(str(e)))

    def get_download_path(self):
        """Determine the download folder path"""
        if platform == 'android':
            # Try external storage
            ext = os.environ.get('EXTERNAL_STORAGE', '/sdcard')
            # Try possible Download paths
            possible_paths = [
                os.path.join(ext, 'Download', 'ms'),
                os.path.join(ext, 'download', 'ms'),
                os.path.join(os.path.expanduser('~'), 'storage', 'emulated', '0', 'Download', 'ms'),
                os.path.join(os.path.expanduser('~'), 'Downloads', 'ms'),
            ]
            for path in possible_paths:
                try:
                    os.makedirs(path, exist_ok=True)
                    # Test write access
                    test_file = os.path.join(path, '.write_test')
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    return path
                except Exception as e:
                    Logger.debug('Path {} not writable: {}'.format(path, str(e)))
                    continue
            # Fallback: app internal folder
            app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ms_images')
            os.makedirs(app_dir, exist_ok=True)
            return app_dir
        else:
            # Desktop
            download_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'ms')
            os.makedirs(download_dir, exist_ok=True)
            return download_dir

    def split_text_into_lines(self, text, max_width, font, draw):
        """Split text into lines based on available width"""
        lines = []
        current_line = ''
        for char in text:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width > max_width and current_line:
                lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        return lines

    def download_images(self, instance):
        text = self.output_label.text
        if not text or text == 'Enter text and press Convert':
            self.status_label.text = 'No text to convert!'
            return

        self.download_btn.disabled = True
        self.status_label.text = 'Preparing images...'

        # Run in separate thread to avoid UI freeze
        from threading import Thread
        Thread(target=self._download_images_thread, args=(text,), daemon=True).start()

    def _download_images_thread(self, text):
        try:
            CHARS_PER_IMAGE = 320
            total_len = len(text)
            parts = []
            for i in range(0, total_len, CHARS_PER_IMAGE):
                parts.append(text[i:i+CHARS_PER_IMAGE])

            # Save path
            save_dir = self.get_download_path()
            os.makedirs(save_dir, exist_ok=True)

            # Delete old images (optional)
            try:
                for f in os.listdir(save_dir):
                    if f.endswith('.png') and f.startswith('musnad_page_'):
                        try:
                            os.remove(os.path.join(save_dir, f))
                        except:
                            pass
            except Exception as e:
                Logger.warning('Could not clean old images: {}'.format(str(e)))

            # Prepare font
            font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ms.ttf')
            if not os.path.exists(font_path):
                # Try assets folder
                alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'ms.ttf')
                if os.path.exists(alt_path):
                    font_path = alt_path
                else:
                    Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Error: ms.ttf font file not found'), 0)
                    Clock.schedule_once(lambda dt: setattr(self.download_btn, 'disabled', False), 0)
                    return

            font_size = 48
            padding = 40
            bottom_padding = 60
            max_width = 700

            # Create images
            for idx, part in enumerate(parts, start=1):
                # Temporary image for text measurement
                temp_img = PILImage.new('RGB', (1, 1), color='white')
                temp_draw = ImageDraw.Draw(temp_img)
                try:
                    font = ImageFont.truetype(font_path, font_size)
                except:
                    font = ImageFont.load_default()

                # Split into lines
                lines = self.split_text_into_lines(part, max_width - 2*padding, font, temp_draw)
                line_height = font_size + 10
                text_height = len(lines) * line_height
                total_height = text_height + 2*padding + bottom_padding

                # Create final image
                img = PILImage.new('RGB', (max_width, total_height), color='white')
                draw = ImageDraw.Draw(img)

                # Draw text
                y = padding
                for line in lines:
                    draw.text((max_width - padding, y), line, font=font, fill='black', anchor='ra')
                    y += line_height

                # Draw page number
                number_text = 'Image {} of {}'.format(idx, len(parts))
                draw.text((max_width//2, total_height - 10), number_text, font=ImageFont.load_default(), fill='#6d4c3a', anchor='ms')

                # Save image
                filename = 'musnad_page_{}.png'.format(idx)
                filepath = os.path.join(save_dir, filename)
                img.save(filepath, 'PNG')

            message = 'Saved {} images to {}'.format(len(parts), save_dir)
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', message), 0)
            Clock.schedule_once(lambda dt: setattr(self.download_btn, 'disabled', False), 0)

        except Exception as e:
            Logger.exception('Error in download_images_thread')
            error_msg = 'Error: {}'.format(str(e))
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', error_msg), 0)
            Clock.schedule_once(lambda dt: setattr(self.download_btn, 'disabled', False), 0)

if __name__ == '__main__':
    MusnadConverterApp().run()
