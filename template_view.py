"""
template_view.py — Workout Template Selection UI
Popup-based interface for loading, saving, and managing workout templates.
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.app import App

from template_manager import TemplateManager


class TemplateView:
    """Manages the template selection popup."""

    def __init__(self):
        self.manager = TemplateManager()
        self.popup = None

    def show_load_popup(self, on_select_callback):
        """
        Show popup to select and load a template.

        Args:
            on_select_callback: Function called with (template) when user selects one
        """
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(18))

        # Title
        content.add_widget(Label(
            text="WORKOUT TEMPLATES",
            font_size='18sp', bold=True,
            color=(0.2, 1.0, 0.6, 1),
            size_hint_y=None, height=dp(30)
        ))

        # Template list (scrollable)
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True, bar_width=0)
        list_box = BoxLayout(
            orientation='vertical', spacing=dp(8),
            size_hint_y=None, height=self.manager.count * dp(110) + dp(20)
        )

        if self.manager.count == 0:
            list_box.height = dp(80)  # Ensure enough space for empty message
            list_box.add_widget(Label(
                text="No templates saved yet.\nComplete a workout and save it as a template.",
                font_size='13sp', color=(0.5, 0.5, 0.5, 1),
                halign='center', valign='middle',
                text_size=(dp(280), None),
                size_hint_y=None, height=dp(70)
            ))
        else:
            for i, template in enumerate(self.manager.templates):
                card = self._make_template_card(template, i, on_select_callback)
                list_box.add_widget(card)

        scroll.add_widget(list_box)
        content.add_widget(scroll)

        # Close button
        close_btn = Button(
            text="CLOSE", bold=True, font_size='13sp',
            size_hint_y=None, height=dp(42),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0),
            color=(0.6, 0.6, 0.6, 1),
            border=(0, 0, 0, 0)
        )
        with close_btn.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.18, 0.18, 0.18, 1)
            RoundedRectangle(pos=close_btn.pos, size=close_btn.size, radius=[dp(14)])
        close_btn.bind(pos=lambda inst, val: self._redraw_btn(inst, (0.18, 0.18, 0.18, 1)))
        close_btn.bind(size=lambda inst, val: self._redraw_btn(inst, (0.18, 0.18, 0.18, 1)))
        close_btn.bind(on_press=lambda x: self.popup.dismiss())
        content.add_widget(close_btn)

        # Fixed popup height — ScrollView handles the overflow
        self.popup = Popup(
            title="", content=content,
            size_hint=(0.88, 0.75),
            auto_dismiss=True,
            background_color=(0.1, 0.1, 0.1, 0.95),
            separator_height=0
        )
        self.popup.open()

    def _make_template_card(self, template, index, on_select_callback):
        """Create a card widget for a single template."""
        self._on_select_callback = on_select_callback
        card = BoxLayout(
            orientation='vertical', spacing=dp(6),
            padding=[dp(14), dp(10), dp(14), dp(10)],
            size_hint_y=None, height=dp(100)
        )
        with card.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.15, 0.15, 0.15, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=lambda inst, val: self._redraw_card_bg(inst), size=lambda inst, val: self._redraw_card_bg(inst))

        # Row 1: Name + LOAD button on same line
        row1 = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(32))
        row1.add_widget(Label(
            text=template.name,
            font_size='14sp', bold=True,
            color=(1, 1, 1, 1),
            halign='left', valign='middle',
            text_size=(None, None),
            shorten=True, shorten_from='right',
            size_hint_x=0.65
        ))
        load_btn = Button(
            text="LOAD", bold=True, font_size='12sp',
            size_hint_x=0.35, size_hint_y=None, height=dp(30),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0),
            color=(0.07, 0.07, 0.07, 1),
            border=(0, 0, 0, 0)
        )
        with load_btn.canvas.before:
            Color(0.2, 1.0, 0.6, 1)
            RoundedRectangle(pos=load_btn.pos, size=load_btn.size, radius=[dp(10)])
        load_btn.bind(pos=lambda inst, val: self._redraw_btn(inst, (0.2, 1.0, 0.6, 1)))
        load_btn.bind(size=lambda inst, val: self._redraw_btn(inst, (0.2, 1.0, 0.6, 1)))
        load_btn.bind(on_press=lambda x, idx=index: self._load_template(idx, on_select_callback))
        row1.add_widget(load_btn)
        card.add_widget(row1)

        # Row 2: Focus + exercise count
        row2 = BoxLayout(size_hint_y=None, height=dp(18))
        row2.add_widget(Label(
            text=f"{template.focus or template.day_type}  |  {template.exercise_count} exercises",
            font_size='10sp', color=(0.2, 1.0, 0.6, 1),
            halign='left', valign='middle',
            text_size=(None, None)
        ))
        card.add_widget(row2)

        # Row 3: RENAME + DELETE
        row3 = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(28))
        rename_btn = Button(
            text="RENAME", bold=True, font_size='10sp',
            size_hint_x=0.5, size_hint_y=None, height=dp(26),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0),
            color=(0.0, 0.8, 1.0, 1),
            border=(0, 0, 0, 0)
        )
        with rename_btn.canvas.before:
            Color(0.0, 0.8, 1.0, 0.15)
            RoundedRectangle(pos=rename_btn.pos, size=rename_btn.size, radius=[dp(8)])
        rename_btn.bind(pos=lambda inst, val: self._redraw_btn(inst, (0.0, 0.8, 1.0, 0.15)))
        rename_btn.bind(size=lambda inst, val: self._redraw_btn(inst, (0.0, 0.8, 1.0, 0.15)))
        rename_btn.bind(on_press=lambda x, idx=index, n=template.name: self._rename_template(idx, n, on_select_callback))
        row3.add_widget(rename_btn)

        delete_btn = Button(
            text="DELETE", bold=True, font_size='10sp',
            size_hint_x=0.5, size_hint_y=None, height=dp(26),
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0),
            color=(1.0, 0.4, 0.4, 1),
            border=(0, 0, 0, 0)
        )
        with delete_btn.canvas.before:
            Color(1.0, 0.4, 0.4, 0.15)
            RoundedRectangle(pos=delete_btn.pos, size=delete_btn.size, radius=[dp(8)])
        delete_btn.bind(pos=lambda inst, val: self._redraw_btn(inst, (1.0, 0.4, 0.4, 0.15)))
        delete_btn.bind(size=lambda inst, val: self._redraw_btn(inst, (1.0, 0.4, 0.4, 0.15)))
        delete_btn.bind(on_press=lambda x, idx=index: self._delete_template(idx, on_select_callback))
        row3.add_widget(delete_btn)

        card.add_widget(row3)
        return card

    def _load_template(self, index, callback):
        """Load a template and call the callback."""
        template = self.manager.load_template(index)
        if template and self.popup:
            self.popup.dismiss()
            callback(template)

    def _delete_template(self, index, callback):
        """Delete a template after confirmation."""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label

        template = self.manager.load_template(index)
        if not template:
            return

        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(18))
        content.add_widget(Label(
            text="DELETE ROUTINE",
            font_size='16sp', bold=True,
            color=(1.0, 0.4, 0.4, 1),
            size_hint_y=None, height=dp(28)
        ))
        content.add_widget(Label(
            text=f'Are you sure you want to delete "{template.name}"?',
            font_size='13sp', color=(1, 1, 1, 1),
            size_hint_y=None, height=dp(22)
        ))

        btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(40))

        cancel = Button(text="CANCEL", bold=True, font_size='12sp',
            background_normal='', background_down='', background_color=(0,0,0,0),
            color=(0.6, 0.6, 0.6, 1), border=(0,0,0,0))
        with cancel.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.18, 0.18, 0.18, 1)
            RoundedRectangle(pos=cancel.pos, size=cancel.size, radius=[dp(14)])
        cancel.bind(pos=lambda inst, val: self._redraw_btn(inst, (0.18, 0.18, 0.18, 1)))
        cancel.bind(size=lambda inst, val: self._redraw_btn(inst, (0.18, 0.18, 0.18, 1)))
        btn_row.add_widget(cancel)

        confirm = Button(text="DELETE", bold=True, font_size='12sp',
            background_normal='', background_down='', background_color=(0,0,0,0),
            color=(0.07, 0.07, 0.07, 1), border=(0,0,0,0))
        with confirm.canvas.before:
            Color(1.0, 0.4, 0.4, 1)
            RoundedRectangle(pos=confirm.pos, size=confirm.size, radius=[dp(14)])
        confirm.bind(pos=lambda inst, val: self._redraw_btn(inst, (1.0, 0.4, 0.4, 1)))
        confirm.bind(size=lambda inst, val: self._redraw_btn(inst, (1.0, 0.4, 0.4, 1)))
        btn_row.add_widget(confirm)

        content.add_widget(btn_row)

        confirm_popup = Popup(title="", content=content, size_hint=(0.75, None), height=dp(170),
            auto_dismiss=True, background_color=(0.1, 0.1, 0.1, 0.95), separator_height=0)

        def do_delete(x):
            self.manager.delete_template(index)
            confirm_popup.dismiss()
            self.popup.dismiss()
            self.show_load_popup(callback)

        confirm.bind(on_press=do_delete)
        cancel.bind(on_press=lambda x: confirm_popup.dismiss())
        confirm_popup.open()

    def _rename_template(self, index, current_name, callback):
        """Rename a template."""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.uix.textinput import TextInput

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(18))
        content.add_widget(Label(
            text="RENAME ROUTINE",
            font_size='16sp', bold=True,
            color=(0.0, 0.8, 1.0, 1),
            size_hint_y=None, height=dp(28)
        ))
        name_input = TextInput(
            text=current_name, font_size='14sp',
            size_hint_y=None, height=dp(40),
            background_normal='', background_active='',
            background_color=(0.15, 0.15, 0.15, 1),
            cursor_color=(0.2, 1.0, 0.6, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.4, 0.4, 0.4, 1),
            padding=[dp(12), dp(8)],
            multiline=False
        )
        content.add_widget(name_input)

        btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(40))

        cancel = Button(text="CANCEL", bold=True, font_size='12sp',
            background_normal='', background_down='', background_color=(0,0,0,0),
            color=(0.6, 0.6, 0.6, 1), border=(0,0,0,0))
        with cancel.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.18, 0.18, 0.18, 1)
            RoundedRectangle(pos=cancel.pos, size=cancel.size, radius=[dp(14)])
        cancel.bind(pos=lambda inst, val: self._redraw_btn(inst, (0.18, 0.18, 0.18, 1)))
        cancel.bind(size=lambda inst, val: self._redraw_btn(inst, (0.18, 0.18, 0.18, 1)))
        btn_row.add_widget(cancel)

        save = Button(text="SAVE", bold=True, font_size='12sp',
            background_normal='', background_down='', background_color=(0,0,0,0),
            color=(0.07, 0.07, 0.07, 1), border=(0,0,0,0))
        with save.canvas.before:
            Color(0.0, 0.8, 1.0, 1)
            RoundedRectangle(pos=save.pos, size=save.size, radius=[dp(14)])
        save.bind(pos=lambda inst, val: self._redraw_btn(inst, (0.0, 0.8, 1.0, 1)))
        save.bind(size=lambda inst, val: self._redraw_btn(inst, (0.0, 0.8, 1.0, 1)))
        btn_row.add_widget(save)

        content.add_widget(btn_row)

        rename_popup = Popup(title="", content=content, size_hint=(0.75, None), height=dp(190),
            auto_dismiss=True, background_color=(0.1, 0.1, 0.1, 0.95), separator_height=0)

        def do_rename(x):
            new_name = name_input.text.strip()
            if new_name:
                self.manager.rename_template(index, new_name)
            rename_popup.dismiss()
            self.popup.dismiss()
            self.show_load_popup(callback)

        save.bind(on_press=do_rename)
        cancel.bind(on_press=lambda x: rename_popup.dismiss())
        rename_popup.open()

    def _redraw_btn(self, inst, color):
        """Redraw a button's background."""
        inst.canvas.before.clear()
        with inst.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(10)])

    def _redraw_card_bg(self, inst):
        """Redraw a template card's background."""
        inst.canvas.before.clear()
        with inst.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.15, 0.15, 0.15, 1)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])

    def show_save_popup(self, session_data, on_save_callback=None):
        """
        Show popup to save current workout as a template.

        Args:
            session_data: Current workout session data dict
            on_save_callback: Optional callback after saving
        """
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(18))

        # Title
        content.add_widget(Label(
            text="SAVE ROUTINE",
            font_size='18sp', bold=True,
            color=(0.2, 1.0, 0.6, 1),
            size_hint_y=None, height=dp(30)
        ))

        # Name input
        content.add_widget(Label(
            text="Template Name",
            font_size='12sp', color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None, height=dp(18),
            halign='left'
        ))
        name_input = TextInput(
            hint_text="e.g., Push Day A",
            font_size='14sp',
            size_hint_y=None, height=dp(44),
            background_normal='', background_active='',
            background_color=(0.15, 0.15, 0.15, 1),
            cursor_color=(0.2, 1.0, 0.6, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.4, 0.4, 0.4, 1),
            padding=[dp(12), dp(10)]
        )
        content.add_widget(name_input)

        # Exercise preview
        ex_count = len(session_data.get("exercises", []))
        focus = session_data.get("focus", "Workout")
        content.add_widget(Label(
            text=f"Saving {ex_count} exercises from: {focus}",
            font_size='12sp', color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None, height=dp(20)
        ))

        # Buttons
        btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(44))

        cancel_btn = Button(
            text="CANCEL", bold=True, font_size='13sp',
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0),
            color=(0.6, 0.6, 0.6, 1),
            border=(0, 0, 0, 0)
        )
        with cancel_btn.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.18, 0.18, 0.18, 1)
            RoundedRectangle(pos=cancel_btn.pos, size=cancel_btn.size, radius=[dp(14)])
        cancel_btn.bind(pos=lambda inst, val: self._redraw_btn(inst, (0.18, 0.18, 0.18, 1)))
        cancel_btn.bind(size=lambda inst, val: self._redraw_btn(inst, (0.18, 0.18, 0.18, 1)))
        cancel_btn.bind(on_press=lambda x: self.popup.dismiss())
        btn_row.add_widget(cancel_btn)

        save_btn = Button(
            text="SAVE ROUTINE", bold=True, font_size='13sp',
            background_normal='', background_down='',
            background_color=(0, 0, 0, 0),
            color=(0.07, 0.07, 0.07, 1),
            border=(0, 0, 0, 0)
        )
        with save_btn.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.2, 1.0, 0.6, 1)
            RoundedRectangle(pos=save_btn.pos, size=save_btn.size, radius=[dp(14)])
        save_btn.bind(pos=lambda inst, val: self._redraw_btn(inst, (0.2, 1.0, 0.6, 1)))
        save_btn.bind(size=lambda inst, val: self._redraw_btn(inst, (0.2, 1.0, 0.6, 1)))
        save_btn.bind(on_press=lambda x: self._do_save(name_input.text, session_data, on_save_callback))
        btn_row.add_widget(save_btn)

        content.add_widget(btn_row)

        self.popup = Popup(
            title="", content=content,
            size_hint=(0.85, None), height=dp(280),
            auto_dismiss=True,
            background_color=(0.1, 0.1, 0.1, 0.95),
            separator_height=0
        )
        self.popup.open()

    def _do_save(self, name, session_data, callback):
        """Save the template."""
        if not name.strip():
            name = f"Workout {self.manager.count + 1}"

        self.manager.save_from_session(name.strip(), session_data)
        if self.popup:
            self.popup.dismiss()
        if callback:
            callback()
