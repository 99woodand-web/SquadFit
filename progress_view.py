# progress_view.py - Progress tracking with charts, PRs, and calendar heatmap
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle


class ProgressScreen(BoxLayout):
    """Progress tracking screen with charts, PR timeline, and calendar heatmap."""
    
    current_tab = StringProperty("charts")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._workout_history = self._load_workout_history()
        self._completions = self._load_completions()
        Clock.schedule_once(self._init_ui, 0.1)
    
    def _init_ui(self, dt):
        """Initialize the UI after KV is loaded."""
        # Set up tab redraw bindings once (so they don't accumulate)
        for tab_id in ['tab_charts', 'tab_prs', 'tab_calendar']:
            if hasattr(self.ids, tab_id):
                btn = self.ids[tab_id]
                btn.bind(pos=lambda inst, val: self._update_tab_bg(inst))
                btn.bind(size=lambda inst, val: self._update_tab_bg(inst))
        self.switch_tab('charts')
    
    # ═══════════════════════════════════════════════════════════════
    #  DATA LOADING
    # ═══════════════════════════════════════════════════════════════
    def _load_workout_history(self):
        """Build workout history from completions (grouped by exercise + date)."""
        from collections import defaultdict
        history = defaultdict(list)
        for c in self._load_completions():
            date = c.get('date', '')
            for s in c.get('sets', []):
                ex_name = s.get('exercise', '')
                if ex_name:
                    history[ex_name].append({
                        'exercise': ex_name,
                        'reps': s.get('reps', 0),
                        'date': date,
                        'set': s.get('set', 0)
                    })
        return dict(history)
    
    def _load_completions(self):
        """Load workout completions from JSON file."""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workout_completions.json')
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        return data if isinstance(data, list) else []
        except Exception:
            pass
        return []

    def _build_exercises_from_completions(self):
        """Build exercise data from workout completions if history is empty."""
        from collections import defaultdict
        exercises = defaultdict(list)
        for c in self._completions:
            for s in c.get('sets', []):
                ex_name = s.get('exercise', '')
                if ex_name:
                    exercises[ex_name].append({
                        'exercise': ex_name,
                        'reps': s.get('reps', 0),
                        'date': c.get('date', ''),
                        'sets': 1
                    })
        return list(exercises.items())

    def export_history_csv(self):
        """Export all workout history to a CSV file."""
        import csv
        import os
        from datetime import datetime
        from kivy.app import App
        app = App.get_running_app()

        completions = self._load_completions()
        if not completions:
            if hasattr(app, 'sm'):
                pw = app.sm.get_screen('progress').children[0]
                if hasattr(pw, 'ids') and hasattr(pw.ids, 'lbl_status'):
                    pw.ids.lbl_status.text = "No workouts to export!"
            return

        # Build CSV rows
        rows = []
        for entry in completions:
            date = entry.get('date', '')
            name = entry.get('workout_name', '')
            elapsed = entry.get('elapsed', 0)
            mins = elapsed // 60
            secs = elapsed % 60
            duration = f"{mins:02d}:{secs:02d}"

            sets = entry.get('sets', [])
            if sets:
                for s in sets:
                    rows.append({
                        'Date': date,
                        'Workout': name,
                        'Duration': duration,
                        'Exercise': s.get('exercise', ''),
                        'Set': s.get('set', ''),
                        'Reps': s.get('reps', s.get('distance', '')),
                        'Type': s.get('type', 'strength'),
                    })
            else:
                rows.append({
                    'Date': date,
                    'Workout': name,
                    'Duration': duration,
                    'Exercise': '',
                    'Set': '',
                    'Reps': '',
                    'Type': '',
                })

        # Write CSV
        csv_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'squadfit_history.csv')
        # Fallback to app directory if Downloads doesn't exist
        if not os.path.isdir(os.path.dirname(csv_path)):
            csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'squadfit_history.csv')

        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Date', 'Workout', 'Duration', 'Exercise', 'Set', 'Reps', 'Type'])
                writer.writeheader()
                writer.writerows(rows)
            print(f"[Progress] Exported {len(rows)} rows to {csv_path}")
            # Show confirmation
            if hasattr(app, 'sm'):
                pw = app.sm.get_screen('progress').children[0]
                if hasattr(pw, 'ids') and hasattr(pw.ids, 'lbl_status'):
                    pw.ids.lbl_status.text = f"Exported {len(rows)} rows to CSV!"
        except Exception as e:
            print(f"[Progress] Export error: {e}")
            if hasattr(app, 'sm'):
                pw = app.sm.get_screen('progress').children[0]
                if hasattr(pw, 'ids') and hasattr(pw.ids, 'lbl_status'):
                    pw.ids.lbl_status.text = f"Export failed: {e}"
    
    # ═══════════════════════════════════════════════════════════════
    #  TAB SWITCHING
    # ═══════════════════════════════════════════════════════════════
    def switch_tab(self, tab_name):
        """Switch between Charts, PRs, and Calendar tabs."""
        # Refresh data from disk so completed workouts always show
        self._workout_history = self._load_workout_history()
        self._completions = self._load_completions()
        self.current_tab = tab_name
        
        # Update tab button styles
        from kivy.app import App
        app = App.get_running_app()
        
        for tab_id, name in [('tab_charts', 'charts'), ('tab_prs', 'prs'), ('tab_calendar', 'calendar')]:
            if hasattr(self.ids, tab_id):
                btn = self.ids[tab_id]
                is_active = (name == tab_name)
                btn.color = (0.07, 0.07, 0.07, 1) if is_active else (0.8, 0.8, 0.8, 1)
                btn.md_bg_color = app.accent_color if is_active else app.card_bg
                btn.canvas.before.clear()
                with btn.canvas.before:
                    Color(*app.accent_color if is_active else app.card_bg)
                    RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(12)])
                # Store tab name on the button for dynamic redraw
                btn._tab_name = name
        
        # Build content
        content = self.ids.content_area
        content.clear_widgets()
        
        if tab_name == 'charts':
            self._build_charts_tab(content)
        elif tab_name == 'prs':
            self._build_prs_tab(content)
        elif tab_name == 'calendar':
            self._build_calendar_tab(content)
    
    def _redraw_tab(self, inst, color):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])

    def _update_tab_bg(self, inst):
        """Redraw tab background based on current active tab."""
        from kivy.app import App
        app = App.get_running_app()
        tab_name = getattr(inst, '_tab_name', '')
        is_active = (tab_name == self.current_tab)
        color = app.accent_color if is_active else app.card_bg
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*color)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])
    
    # ═══════════════════════════════════════════════════════════════
    #  TAB 1: EXERCISE PROGRESS CHARTS
    # ═══════════════════════════════════════════════════════════════
    def _build_charts_tab(self, container):
        """Build the exercise progress charts view."""
        from kivy.app import App
        app = App.get_running_app()
        
        # Get exercises with history
        exercises_with_data = []
        for ex_name, sessions in self._workout_history.items():
            if len(sessions) >= 1:  # Show even 1 session
                exercises_with_data.append((ex_name, sessions))
        
        # Also build from completions if history is empty
        if not exercises_with_data:
            exercises_with_data = self._build_exercises_from_completions()
        
        if not exercises_with_data:
            container.add_widget(Label(
                text="No exercise data yet.\nComplete workouts to see progress charts!",
                font_size='14sp', color=(0.5, 0.5, 0.5, 1),
                halign='center', valign='middle',
                size_hint_y=None, height=dp(100)
            ))
            return
        
        # Section header
        container.add_widget(Label(
            text=f"EXERCISE PROGRESS ({len(exercises_with_data)} exercises)",
            font_size='12sp', bold=True, color=(0.5, 0.5, 0.5, 1),
            halign='left', size_hint_y=None, height=dp(24),
            padding=[dp(4), 0]
        ))
        
        # Weekly volume bar chart (summary)
        weekly_chart = self._build_weekly_volume_chart(app)
        container.add_widget(weekly_chart)

        # Build a chart card for each exercise
        for ex_name, sessions in exercises_with_data[:10]:  # Show top 10
            card = self._build_chart_card(ex_name, sessions, app)
            container.add_widget(card)
    
    def _build_chart_card(self, exercise_name, sessions, app):
        """Build a single exercise chart card."""
        card = BoxLayout(
            orientation='vertical', spacing=dp(6),
            padding=dp(12), size_hint_y=None, height=dp(180)
        )
        with card.canvas.before:
            Color(*app.card_bg)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=lambda inst, val: self._redraw_card(inst, app))
        card.bind(size=lambda inst, val: self._redraw_card(inst, app))
        
        # Exercise name
        card.add_widget(Label(
            text=exercise_name, font_size='14sp', bold=True,
            color=(1, 1, 1, 1), halign='left', size_hint_y=None, height=dp(22)
        ))
        
        # Chart widget
        chart = ExerciseChart(
            sessions=sessions, size_hint_y=None, height=dp(120)
        )
        card.add_widget(chart)
        
        # Stats row
        stats = self._calculate_stats(sessions)
        stats_label = Label(
            text=f"Best: {stats['best_reps']} reps | Latest: {stats['latest_reps']} reps | Sessions: {stats['session_count']}",
            font_size='10sp', color=(0.6, 0.6, 0.6, 1),
            halign='left', size_hint_y=None, height=dp(18)
        )
        card.add_widget(stats_label)
        
        return card
    
    def _redraw_card(self, inst, app):
        inst.canvas.before.clear()
        with inst.canvas.before:
            Color(*app.card_bg)
            RoundedRectangle(pos=inst.pos, size=inst.size, radius=[dp(12)])
    
    def _calculate_stats(self, sessions):
        """Calculate stats for an exercise."""
        total_reps = []
        for s in sessions:
            r = s.get('reps', 0)
            if isinstance(r, (int, float)) and r > 0:
                total_reps.append(r)
            elif isinstance(r, str):
                try:
                    val = int(r.replace(' reps', '').strip())
                    if val > 0:
                        total_reps.append(val)
                except (ValueError, TypeError):
                    pass
        
        return {
            'best_reps': max(total_reps) if total_reps else 0,
            'latest_reps': total_reps[-1] if total_reps else 0,
            'session_count': len(sessions),
            'total_reps': sum(total_reps)
        }
    
    def _build_weekly_volume_chart(self, app):
        """Build a bar chart showing total volume per week for the last 8 weeks."""
        # Aggregate volume by week
        from datetime import datetime, timedelta
        today = datetime.now()
        weekly_volumes = []

        for w in range(7, -1, -1):  # Last 8 weeks
            week_end = today - timedelta(days=today.weekday()) - timedelta(weeks=w)
            week_start = week_end - timedelta(days=6)
            week_start_str = week_start.strftime('%Y-%m-%d')
            week_end_str = week_end.strftime('%Y-%m-%d')

            vol = 0
            for ex_name, sessions in self._workout_history.items():
                for s in sessions:
                    date = s.get('date', '')[:10]
                    reps = s.get('reps', 0)
                    if isinstance(reps, str):
                        try:
                            reps = int(reps.replace(' reps', '').strip())
                        except (ValueError, TypeError):
                            reps = 0
                    if week_start_str <= date <= week_end_str and isinstance(reps, (int, float)) and reps > 0:
                        vol += reps

            label = week_start.strftime('%d %b')
            weekly_volumes.append({'label': label, 'volume': vol})

        chart = WeeklyVolumeChart(data=weekly_volumes, size_hint_y=None, height=dp(150))
        return chart

    # ═══════════════════════════════════════════════════════════════
    #  TAB 2: PR TIMELINE
    # ═══════════════════════════════════════════════════════════════
    def _build_prs_tab(self, container):
        """Build the PR timeline view."""
        from kivy.app import App
        app = App.get_running_app()
        
        prs = self._detect_all_prs()
        
        if not prs:
            container.add_widget(Label(
                text="No personal records yet.\nComplete workouts to start tracking PRs!",
                font_size='14sp', color=(0.5, 0.5, 0.5, 1),
                halign='center', valign='middle',
                size_hint_y=None, height=dp(100)
            ))
            return
        
        # Section header
        container.add_widget(Label(
            text=f"PERSONAL RECORDS ({len(prs)} total)",
            font_size='12sp', bold=True, color=(0.5, 0.5, 0.5, 1),
            halign='left', size_hint_y=None, height=dp(24),
            padding=[dp(4), 0]
        ))
        
        # Build PR cards
        for pr in prs:
            card = self._build_pr_card(pr, app)
            container.add_widget(card)
    
    def _detect_all_prs(self):
        """Detect personal records for all exercises."""
        from collections import defaultdict
        prs = []
        
        # Group sessions by date to get per-session totals
        for ex_name, sessions in self._workout_history.items():
            daily_totals = defaultdict(int)
            daily_dates = {}
            for s in sessions:
                r = s.get('reps', 0)
                if isinstance(r, str):
                    try:
                        r = int(r.replace(' reps', '').strip())
                    except (ValueError, TypeError):
                        r = 0
                if isinstance(r, (int, float)) and r > 0:
                    date_key = s.get('date', '')[:10]
                    daily_totals[date_key] += r
                    daily_dates[date_key] = s.get('date', '')[:10]
            
            if daily_totals:
                best_date = max(daily_totals, key=daily_totals.get)
                prs.append({
                    'exercise': ex_name,
                    'reps': daily_totals[best_date],
                    'date': daily_dates.get(best_date, '')
                })
        
        # Sort by reps (highest first)
        prs.sort(key=lambda x: x.get('reps', 0), reverse=True)
        return prs
    
    def _build_pr_card(self, pr, app):
        """Build a single PR card."""
        card = BoxLayout(
            orientation='horizontal', spacing=dp(10),
            padding=dp(12), size_hint_y=None, height=dp(60)
        )
        with card.canvas.before:
            Color(*app.card_bg)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(pos=lambda inst, val: self._redraw_card(inst, app))
        card.bind(size=lambda inst, val: self._redraw_card(inst, app))
        
        # Trophy icon
        trophy = Label(
            text="PR", font_size='14sp', bold=True,
            color=(1.0, 0.84, 0.0, 1),  # Gold
            size_hint_x=None, width=dp(40)
        )
        card.add_widget(trophy)
        
        # Exercise info
        info_box = BoxLayout(orientation='vertical', spacing=dp(2))
        info_box.add_widget(Label(
            text=pr['exercise'], font_size='13sp', bold=True,
            color=(1, 1, 1, 1), halign='left'
        ))
        info_box.add_widget(Label(
            text=f"{pr['reps']} total reps",
            font_size='11sp', color=(0.2, 1.0, 0.6, 1), halign='left'
        ))
        card.add_widget(info_box)
        
        # Date
        card.add_widget(Label(
            text=pr['date'], font_size='10sp',
            color=(0.5, 0.5, 0.5, 1), halign='right',
            size_hint_x=None, width=dp(80)
        ))
        
        return card
    
    # ═══════════════════════════════════════════════════════════════
    #  TAB 3: WORKOUT CALENDAR HEATMAP
    # ═══════════════════════════════════════════════════════════════
    def _build_calendar_tab(self, container):
        """Build the workout calendar heatmap view."""
        from kivy.app import App
        app = App.get_running_app()
        
        # Get workout dates
        workout_dates = self._get_workout_dates()
        
        # Section header
        container.add_widget(Label(
            text="WORKOUT CALENDAR",
            font_size='12sp', bold=True, color=(0.5, 0.5, 0.5, 1),
            halign='left', size_hint_y=None, height=dp(24),
            padding=[dp(4), 0]
        ))
        
        # Calendar heatmap
        calendar_widget = CalendarHeatmap(
            workout_dates=workout_dates, size_hint_y=None, height=dp(200)
        )
        container.add_widget(calendar_widget)
        
        # Stats
        stats = self._calculate_calendar_stats(workout_dates)
        stats_box = BoxLayout(
            orientation='horizontal', spacing=dp(10),
            size_hint_y=None, height=dp(60)
        )
        
        for label, value in [
            ("This Week", str(stats['this_week'])),
            ("This Month", str(stats['this_month'])),
            ("Current Streak", f"{stats['streak']} days"),
            ("Total Workouts", str(stats['total']))
        ]:
            stat_card = BoxLayout(
                orientation='vertical', spacing=dp(2),
                padding=dp(8)
            )
            with stat_card.canvas.before:
                Color(*app.card_bg)
                RoundedRectangle(pos=stat_card.pos, size=stat_card.size, radius=[dp(8)])
            stat_card.bind(pos=lambda inst, val: self._redraw_card(inst, app))
            stat_card.bind(size=lambda inst, val: self._redraw_card(inst, app))
            
            stat_card.add_widget(Label(
                text=value, font_size='18sp', bold=True,
                color=app.accent_color
            ))
            stat_card.add_widget(Label(
                text=label, font_size='9sp',
                color=(0.5, 0.5, 0.5, 1)
            ))
            stats_box.add_widget(stat_card)
        
        container.add_widget(stats_box)
    
    def _get_workout_dates(self):
        """Get unique workout dates from completions and history."""
        dates = set()
        
        # From completions
        for c in self._completions:
            date = c.get('date', '')
            if date:
                dates.add(date)
        
        # From history
        for ex_name, sessions in self._workout_history.items():
            for s in sessions:
                date = s.get('date', '')[:10]
                if date:
                    dates.add(date)
        
        return dates
    
    def _calculate_calendar_stats(self, workout_dates):
        """Calculate calendar statistics."""
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        
        # This week
        week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        this_week = sum(1 for d in workout_dates if week_start <= d <= today_str)
        
        # This month
        month_start = today.strftime('%Y-%m-01')
        this_month = sum(1 for d in workout_dates if month_start <= d <= today_str)
        
        # Total
        total = len(workout_dates)
        
        # Streak
        streak = 0
        check_date = today
        while check_date.strftime('%Y-%m-%d') in workout_dates:
            streak += 1
            check_date -= timedelta(days=1)
        
        return {
            'this_week': this_week,
            'this_month': this_month,
            'streak': streak,
            'total': total
        }
    
    def go_back(self):
        """Navigate back to calendar."""
        try:
            from kivy.app import App
            app = App.get_running_app()
            if hasattr(app, 'sm'):
                app.sm.current = 'calendar'
        except Exception as e:
            print(f"[Navigation Error] {e}")


class ExerciseChart(Widget):
    """Custom widget that draws an exercise progress line chart using Kivy Canvas."""
    
    def __init__(self, sessions=None, **kwargs):
        super().__init__(**kwargs)
        self.sessions = sessions or []
        self.bind(pos=self._draw_chart)
        self.bind(size=self._draw_chart)
        Clock.schedule_once(lambda dt: self._draw_chart(), 0.1)
    
    def _draw_chart(self, *args):
        """Draw the line chart on the canvas."""
        self.canvas.clear()
        
        if not self.sessions or len(self.sessions) < 2:
            return
        
        # Extract reps data points
        points = []
        for i, s in enumerate(self.sessions):
            r = s.get('reps', 0)
            if isinstance(r, str):
                try:
                    r = int(r.replace(' reps', '').strip())
                except (ValueError, TypeError):
                    r = 0
            if isinstance(r, (int, float)) and r > 0:
                points.append((i, r))
        
        if len(points) < 2:
            return
        
        # Calculate bounds
        x_vals = [p[0] for p in points]
        y_vals = [p[1] for p in points]
        min_y = min(y_vals) * 0.9
        max_y = max(y_vals) * 1.1
        if max_y == min_y:
            max_y = min_y + 10
        
        # Chart area with padding
        pad_x = dp(40)
        pad_y = dp(10)
        chart_x = self.x + pad_x
        chart_y = self.y + pad_y
        chart_w = self.width - pad_x - dp(10)
        chart_h = self.height - pad_y - dp(20)
        
        with self.canvas:
            # Grid lines
            Color(0.2, 0.2, 0.2, 0.3)
            for i in range(4):
                gy = chart_y + (chart_h * i / 3)
                Line(points=[chart_x, gy, chart_x + chart_w, gy], width=1)
            
            # Y-axis labels
            Color(0.5, 0.5, 0.5, 1)
            for i in range(4):
                gy = chart_y + (chart_h * i / 3)
                val = min_y + (max_y - min_y) * i / 3
            
            # Line chart
            from kivy.app import App
            app = App.get_running_app()
            Color(*app.accent_color)
            
            line_points = []
            for px, py in points:
                x = chart_x + (px / max(x_vals)) * chart_w if max(x_vals) > 0 else chart_x
                y = chart_y + ((py - min_y) / (max_y - min_y)) * chart_h
                line_points.extend([x, y])
            
            if len(line_points) >= 4:
                Line(points=line_points, width=1.5, cap='round', joint='round')
            
            # Data points
            Color(1, 1, 1, 1)
            for px, py in points:
                x = chart_x + (px / max(x_vals)) * chart_w if max(x_vals) > 0 else chart_x
                y = chart_y + ((py - min_y) / (max_y - min_y)) * chart_h
                Color(*app.accent_color)
                Line(circle=(x, y, 3), width=1.5)


class CalendarHeatmap(Widget):
    """Custom widget that draws a workout calendar heatmap using Kivy Canvas."""
    
    def __init__(self, workout_dates=None, **kwargs):
        super().__init__(**kwargs)
        self.workout_dates = workout_dates or set()
        self.bind(pos=self._draw_heatmap)
        self.bind(size=self._draw_heatmap)
        Clock.schedule_once(lambda dt: self._draw_heatmap(), 0.1)
    
    def _draw_heatmap(self, *args):
        """Draw the calendar heatmap on the canvas."""
        self.canvas.clear()
        
        today = datetime.now()
        
        # Draw last 12 weeks (84 days)
        weeks = 12
        days_per_week = 7
        total_days = weeks * days_per_week
        
        # Calculate cell size
        padding = dp(4)
        cell_size = min(
            (self.width - padding * (weeks + 1)) / weeks,
            (self.height - padding * (days_per_week + 1)) / days_per_week,
            dp(20)
        )
        
        # Center the grid
        grid_width = weeks * (cell_size + padding)
        grid_height = days_per_week * (cell_size + padding)
        start_x = self.x + (self.width - grid_width) / 2
        start_y = self.y + (self.height - grid_height) / 2
        
        with self.canvas:
            # Day labels
            Color(0.5, 0.5, 0.5, 1)
            day_labels = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
            
            # Draw cells
            for week in range(weeks):
                for day in range(days_per_week):
                    # Calculate date
                    days_ago = (weeks - 1 - week) * 7 + (6 - day)
                    date = today - timedelta(days=days_ago)
                    date_str = date.strftime('%Y-%m-%d')
                    
                    # Position
                    x = start_x + week * (cell_size + padding)
                    y = start_y + day * (cell_size + padding)
                    
                    # Color based on workout
                    if date_str in self.workout_dates:
                        Color(0.2, 1.0, 0.6, 0.9)  # Green for workout day
                    elif date > today:
                        Color(0.15, 0.15, 0.15, 0.3)  # Future days
                    else:
                        Color(0.15, 0.15, 0.15, 0.8)  # No workout
                    
                    RoundedRectangle(
                        pos=(x, y),
                        size=(cell_size, cell_size),
                        radius=[dp(3)]
                    )
            
            # Month labels
            Color(0.5, 0.5, 0.5, 1)


class WeeklyVolumeChart(Widget):
    """Bar chart showing total volume per week."""

    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data or []
        self.bind(pos=self._draw_chart)
        self.bind(size=self._draw_chart)
        Clock.schedule_once(lambda dt: self._draw_chart(), 0.1)

    def _draw_chart(self, *args):
        self.canvas.clear()
        if not self.data:
            return

        max_vol = max(d['volume'] for d in self.data) if self.data else 1
        if max_vol == 0:
            max_vol = 1

        pad_x = dp(40)
        pad_y = dp(24)
        chart_x = self.x + pad_x
        chart_y = self.y + pad_y
        chart_w = self.width - pad_x - dp(10)
        chart_h = self.height - pad_y - dp(10)

        n = len(self.data)
        bar_w = (chart_w / n) * 0.6 if n > 0 else dp(10)
        gap = (chart_w / n) * 0.4 if n > 0 else dp(5)

        from kivy.app import App
        app = App.get_running_app()

        with self.canvas:
            # Title
            Color(0.5, 0.5, 0.5, 1)

            # Grid lines
            Color(0.2, 0.2, 0.2, 0.3)
            for i in range(4):
                gy = chart_y + (chart_h * i / 3)
                Line(points=[chart_x, gy, chart_x + chart_w, gy], width=0.5)

            # Bars
            for i, d in enumerate(self.data):
                vol = d['volume']
                bar_h = (vol / max_vol) * chart_h if max_vol > 0 else 0
                x = chart_x + i * (bar_w + gap)
                y = chart_y

                # Bar color — brighter for recent weeks
                alpha = 0.4 + (0.6 * (i / max(n - 1, 1)))
                Color(0.2, 1.0, 0.6, alpha)
                RoundedRectangle(pos=(x, y), size=(bar_w, bar_h), radius=[dp(3)])

                # Week label (every other)
                if i % 2 == 0 or n <= 8:
                    Color(0.5, 0.5, 0.5, 1)

            # Y-axis label
            Color(0.5, 0.5, 0.5, 1)

