# main_enhanced_gui.py - Student Tracker with Modern GUI
# Programmed by: Younes Bennacer
# Enhanced Professional Edition

import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle, Ellipse
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import StringProperty, NumericProperty, ListProperty
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('student_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# MODERN COLOR SCHEME - Professional & Elegant
# ============================================
# Primary Colors - Modern Blue Gradient
PRIMARY_DARK = (0.098, 0.278, 0.478, 1)      # Deep blue #19478a
PRIMARY_COLOR = (0.204, 0.459, 0.765, 1)      # Royal blue #3475c3
PRIMARY_LIGHT = (0.282, 0.565, 0.847, 1)      # Sky blue #4890d8

# Accent Colors
ACCENT_COLOR = (0.157, 0.706, 0.647, 1)       # Teal #28b4a5
ACCENT_LIGHT = (0.204, 0.804, 0.741, 1)       # Light teal #34cdbd

# Background Colors
BACKGROUND_DARK = (0.945, 0.953, 0.961, 1)    # Very light gray #f1f3f5
BACKGROUND_COLOR = (0.976, 0.980, 0.984, 1)   # Almost white #f9fafb
CARD_COLOR = (1, 1, 1, 1)                      # Pure white

# Text Colors
TEXT_PRIMARY = (0.098, 0.110, 0.129, 1)       # Dark gray #191c21
TEXT_SECONDARY = (0.435, 0.451, 0.478, 1)     # Medium gray #6f737a
TEXT_LIGHT = (0.647, 0.667, 0.690, 1)         # Light gray #a5aab0

# Semantic Colors
SUCCESS_COLOR = (0.125, 0.749, 0.408, 1)      # Green #20bf68
WARNING_COLOR = (1, 0.643, 0.020, 1)          # Orange #ffa405
ERROR_COLOR = (0.910, 0.176, 0.227, 1)        # Red #e82d3a
INFO_COLOR = (0.204, 0.459, 0.765, 1)         # Blue #3475c3

# Special Colors
HEADER_GRADIENT_START = (0.141, 0.376, 0.647, 1)  # Dark blue
HEADER_GRADIENT_END = (0.204, 0.459, 0.765, 1)    # Royal blue

# UI Element Colors
BUTTON_PRIMARY = PRIMARY_COLOR
BUTTON_SECONDARY = ACCENT_COLOR
BUTTON_HOVER = PRIMARY_LIGHT
SHADOW_COLOR = (0, 0, 0, 0.1)

# ============================================
# CONFIGURATION
# ============================================
class Config:
    """Application configuration"""
    # App Info
    APP_NAME = "Student Tracker Pro"
    APP_VERSION = "2.0"
    DEVELOPER = "Younes Bennacer"
    YEAR = "2024"
    
    # Excel import settings
    POSSIBLE_SHEET_NAMES = ['note', 'noteDataTable1', 'Sheet1', 'Feuil1', 'notes']
    REQUIRED_COLUMNS = ['Matricule', 'Nom', 'Prénom']
    
    # Pagination
    STUDENTS_PER_PAGE = 50
    
    # Backup
    AUTO_BACKUP_INTERVAL = 3600
    BACKUP_FOLDER = 'backups'
    
    # Validation
    MATRICULE_LENGTH = 12
    MIN_SCORE = 0
    MAX_SCORE = 20
    
    # Database
    DB_NAME = 'student_tracker.db'

# ============================================
# UTILITY FUNCTIONS
# ============================================
def validate_matricule(matricule):
    """Validate student matricule format"""
    if not matricule:
        return False, "Matricule cannot be empty"
    
    matricule = str(matricule).strip()
    
    if len(matricule) != Config.MATRICULE_LENGTH:
        return False, f"Matricule must be {Config.MATRICULE_LENGTH} characters"
    
    if not matricule.isdigit():
        return False, "Matricule must contain only numbers"
    
    return True, ""

def validate_score(score):
    """Validate score/grade"""
    if score is None or score == '':
        return True, ""
    
    try:
        score_float = float(score)
        if score_float < Config.MIN_SCORE or score_float > Config.MAX_SCORE:
            return False, f"Score must be between {Config.MIN_SCORE} and {Config.MAX_SCORE}"
        return True, ""
    except ValueError:
        return False, "Score must be a number"

# ============================================
# ENHANCED DATABASE HANDLER
# ============================================
class StudentTrackerDB:
    """Enhanced database handler"""
    
    def __init__(self, db_name=Config.DB_NAME):
        self.db_name = db_name
        self.init_database()
        logger.info(f"Database initialized: {db_name}")
    
    def init_database(self):
        """Initialize database with required tables and indexes"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            # Students table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    matricule TEXT UNIQUE NOT NULL,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    section TEXT,
                    groupe TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Classes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_name TEXT NOT NULL,
                    subject_name TEXT,
                    class_date DATE NOT NULL,
                    groupe TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    class_id INTEGER NOT NULL,
                    status TEXT CHECK(status IN ('Present', 'Absent', 'Absent Justifié')) DEFAULT 'Present',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY(class_id) REFERENCES classes(id) ON DELETE CASCADE,
                    UNIQUE(student_id, class_id)
                )
            ''')
            
            # Marks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS marks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    class_id INTEGER NOT NULL,
                    score REAL CHECK(score >= 0 AND score <= 20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY(class_id) REFERENCES classes(id) ON DELETE CASCADE,
                    UNIQUE(student_id, class_id)
                )
            ''')
            
            # Comments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    class_id INTEGER NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY(class_id) REFERENCES classes(id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_matricule ON students(matricule)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_groupe ON students(groupe)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_marks_student ON marks(student_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_class_date ON classes(class_date)')
            
            conn.commit()
            logger.info("Database tables and indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()
    
    def import_from_excel(self, file_path, groupe_name=None, progress_callback=None):
        """Import student data from Excel file with improved sheet detection"""
        try:
            logger.info(f"Starting Excel import from: {file_path}")
            
            # Try to detect the correct sheet
            xl_file = pd.ExcelFile(file_path)
            sheet_name = None
            
            for possible_name in Config.POSSIBLE_SHEET_NAMES:
                if possible_name in xl_file.sheet_names:
                    sheet_name = possible_name
                    break
            
            if sheet_name is None and xl_file.sheet_names:
                sheet_name = xl_file.sheet_names[0]
                logger.warning(f"Using first available sheet: {sheet_name}")
            else:
                logger.info(f"Found sheet: {sheet_name}")
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            if progress_callback:
                progress_callback(0.1)
            
            # Find the header row containing 'Matricule'
            matricule_col = None
            header_row_idx = 0
            
            for idx, row in df.iterrows():
                for col_idx, cell in enumerate(row):
                    if isinstance(cell, str) and 'Matricule' in cell:
                        header_row_idx = idx
                        matricule_col = col_idx
                        break
                if matricule_col is not None:
                    break
            
            if matricule_col is None:
                error_msg = f"Could not find 'Matricule' column in sheet '{sheet_name}'"
                logger.error(error_msg)
                return False, error_msg, 0
            
            df.columns = df.iloc[header_row_idx]
            df = df[header_row_idx + 1:].reset_index(drop=True)
            
            missing_cols = [col for col in Config.REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                error_msg = f"Missing required columns: {', '.join(missing_cols)}"
                logger.error(error_msg)
                return False, error_msg, 0
            
            if progress_callback:
                progress_callback(0.2)
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            imported_count = 0
            errors = []
            
            total_rows = len(df)
            
            for idx, row in df.iterrows():
                try:
                    if pd.isna(row.get('Matricule')):
                        continue
                    
                    matricule = str(row['Matricule']).strip()
                    
                    is_valid, error_msg = validate_matricule(matricule)
                    if not is_valid:
                        errors.append(f"Row {idx + 1}: {error_msg}")
                        continue
                    
                    nom = str(row.get('Nom', '')).strip()
                    prenom = str(row.get('Prénom', '')).strip()
                    section = str(row.get('Section', '')).strip()
                    groupe = str(row.get('Groupe', '')).strip()
                    
                    if groupe_name:
                        groupe = groupe_name
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO students 
                        (matricule, nom, prenom, section, groupe, updated_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (matricule, nom, prenom, section, groupe))
                    
                    imported_count += 1
                    
                    if progress_callback and idx % 10 == 0:
                        progress = 0.2 + (0.7 * (idx / total_rows))
                        progress_callback(progress)
                    
                except Exception as e:
                    error_msg = f"Row {idx + 1}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    continue
            
            conn.commit()
            conn.close()
            
            if progress_callback:
                progress_callback(1.0)
            
            message = f"Successfully imported {imported_count} students"
            if errors:
                message += f"\nWarnings: {len(errors)} rows skipped"
            
            logger.info(message)
            return True, message, imported_count
            
        except Exception as e:
            error_msg = f"Import error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, 0
    
    def export_to_excel(self, output_path, groupe=None):
        """Export student data to Excel file"""
        try:
            conn = sqlite3.connect(self.db_name)
            
            if groupe:
                query = "SELECT * FROM students WHERE groupe = ? ORDER BY nom, prenom"
                df = pd.read_sql_query(query, conn, params=(groupe,))
            else:
                query = "SELECT * FROM students ORDER BY groupe, nom, prenom"
                df = pd.read_sql_query(query, conn)
            
            conn.close()
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Students', index=False)
            
            message = f"Exported {len(df)} students to {output_path}"
            logger.info(message)
            return True, message
            
        except Exception as e:
            error_msg = f"Export error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def backup_database(self):
        """Create a backup of the database"""
        try:
            if not os.path.exists(Config.BACKUP_FOLDER):
                os.makedirs(Config.BACKUP_FOLDER)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}.db"
            backup_path = os.path.join(Config.BACKUP_FOLDER, backup_name)
            
            import shutil
            shutil.copy2(self.db_name, backup_path)
            
            logger.info(f"Database backed up to: {backup_path}")
            return True, backup_path
            
        except Exception as e:
            error_msg = f"Backup error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def search_students(self, query, groupe=None):
        """Search students by name or matricule"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            search_pattern = f"%{query}%"
            
            if groupe:
                cursor.execute('''
                    SELECT id, matricule, nom, prenom, section, groupe 
                    FROM students 
                    WHERE groupe = ? AND (
                        matricule LIKE ? OR 
                        nom LIKE ? OR 
                        prenom LIKE ?
                    )
                    ORDER BY nom, prenom
                ''', (groupe, search_pattern, search_pattern, search_pattern))
            else:
                cursor.execute('''
                    SELECT id, matricule, nom, prenom, section, groupe 
                    FROM students 
                    WHERE matricule LIKE ? OR nom LIKE ? OR prenom LIKE ?
                    ORDER BY nom, prenom
                ''', (search_pattern, search_pattern, search_pattern))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_students_paginated(self, groupe, page=1, per_page=Config.STUDENTS_PER_PAGE):
        """Get students with pagination"""
        try:
            offset = (page - 1) * per_page
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM students WHERE groupe = ?', (groupe,))
            total_count = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT id, matricule, nom, prenom, section, groupe 
                FROM students 
                WHERE groupe = ? 
                ORDER BY nom, prenom
                LIMIT ? OFFSET ?
            ''', (groupe, per_page, offset))
            
            students = cursor.fetchall()
            conn.close()
            
            total_pages = (total_count + per_page - 1) // per_page
            
            return students, page, total_pages, total_count
            
        except Exception as e:
            logger.error(f"Pagination error: {e}")
            return [], 1, 1, 0
    
    def get_students_by_group(self, groupe):
        """Get all students in a specific group"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, matricule, nom, prenom, section, groupe 
            FROM students 
            WHERE groupe = ? 
            ORDER BY nom, prenom
        ''', (groupe,))
        students = cursor.fetchall()
        conn.close()
        return students
    
    def get_all_groups(self):
        """Get list of all unique groups"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT groupe FROM students WHERE groupe IS NOT NULL ORDER BY groupe')
        groups = [row[0] for row in cursor.fetchall()]
        conn.close()
        return groups
    
    def get_student_stats(self, student_id):
        """Get comprehensive statistics for a student"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
            student = cursor.fetchone()
            
            if not student:
                return None
            
            cursor.execute('''
                SELECT 
                    COUNT(score) as total_marks,
                    AVG(score) as avg_score,
                    MAX(score) as max_score,
                    MIN(score) as min_score
                FROM marks 
                WHERE student_id = ? AND score IS NOT NULL
            ''', (student_id,))
            
            marks_stats = cursor.fetchone()
            
            cursor.execute('''
                SELECT 
                    status,
                    COUNT(*) as count
                FROM attendance 
                WHERE student_id = ?
                GROUP BY status
            ''', (student_id,))
            
            attendance_data = cursor.fetchall()
            attendance_dist = {status: count for status, count in attendance_data}
            
            total_attendance = sum(attendance_dist.values())
            present_count = attendance_dist.get('Present', 0)
            attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0
            
            conn.close()
            
            return {
                'student': student,
                'total_marks': marks_stats[0] or 0,
                'avg_score': round(marks_stats[1], 2) if marks_stats[1] else 0,
                'max_score': marks_stats[2] or 0,
                'min_score': marks_stats[3] or 0,
                'total_classes': total_attendance,
                'present_count': present_count,
                'attendance_rate': round(attendance_rate, 1),
                'attendance_dist': attendance_dist
            }
            
        except Exception as e:
            logger.error(f"Error getting student stats: {e}")
            return None
    
    def delete_student(self, student_id):
        """Delete a student and all related records"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted student {student_id}")
            return True, "Student deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting student: {e}")
            return False, str(e)

# ============================================
# MODERN UI COMPONENTS
# ============================================

class ModernCard(BoxLayout):
    """Modern card with shadow and rounded corners"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = dp(15)
        self.spacing = dp(10)
        
        with self.canvas.before:
            # Shadow
            Color(*SHADOW_COLOR)
            self.shadow = RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(2)),
                size=self.size,
                radius=[dp(12)]
            )
            # Card background
            Color(*CARD_COLOR)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.shadow.pos = (self.x + dp(2), self.y - dp(2))
        self.shadow.size = self.size

class ModernButton(Button):
    """Modern styled button with hover effect"""
    def __init__(self, **kwargs):
        # Extract custom color if provided
        self.button_color = kwargs.pop('button_color', BUTTON_PRIMARY)
        
        super().__init__(**kwargs)
        self.background_color = self.button_color
        self.background_normal = ''
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = sp(14)
        
        # Add rounded corners
        with self.canvas.before:
            Color(*self.button_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_press(self):
        # Subtle press animation
        anim = Animation(background_color=BUTTON_HOVER, duration=0.1)
        anim.start(self)
    
    def on_release(self):
        # Return to original color
        anim = Animation(background_color=self.button_color, duration=0.1)
        anim.start(self)

class ModernLabel(Label):
    """Modern styled label"""
    def __init__(self, title=False, subtitle=False, **kwargs):
        super().__init__(**kwargs)
        
        if title:
            self.font_size = sp(24)
            self.bold = True
            self.color = TEXT_PRIMARY
        elif subtitle:
            self.font_size = sp(16)
            self.bold = True
            self.color = TEXT_SECONDARY
        else:
            self.font_size = sp(14)
            self.color = TEXT_PRIMARY

class GradientHeader(BoxLayout):
    """Beautiful gradient header"""
    def __init__(self, title_text="", **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(100)
        
        # Create gradient background
        with self.canvas.before:
            # Gradient effect (using two rectangles)
            Color(*HEADER_GRADIENT_START)
            self.rect1 = Rectangle(pos=self.pos, size=self.size)
            Color(*HEADER_GRADIENT_END)
            self.rect2 = Rectangle(
                pos=self.pos,
                size=(self.width, self.height / 2)
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Content layout
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(5))
        
        # Title
        title = Label(
            text=title_text,
            font_size=sp(28),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(title)
        
        # Subtitle with developer info
        subtitle = Label(
            text=f'Programmed by {Config.DEVELOPER} © {Config.YEAR}',
            font_size=sp(13),
            color=(1, 1, 1, 0.8),
            size_hint_y=None,
            height=dp(20)
        )
        content.add_widget(subtitle)
        
        # Version
        version = Label(
            text=f'Version {Config.APP_VERSION}',
            font_size=sp(11),
            color=(1, 1, 1, 0.6),
            size_hint_y=None,
            height=dp(15)
        )
        content.add_widget(version)
        
        self.add_widget(content)
    
    def update_rect(self, *args):
        self.rect1.pos = self.pos
        self.rect1.size = self.size
        self.rect2.pos = self.pos
        self.rect2.size = (self.width, self.height / 2)

class SearchBar(BoxLayout):
    """Modern search bar with icon"""
    def __init__(self, on_search=None, on_clear=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.spacing = dp(10)
        
        # Add card background
        with self.canvas.before:
            Color(*CARD_COLOR)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Search icon
        self.add_widget(Label(
            text='🔍',
            size_hint_x=None,
            width=dp(40),
            font_size=sp(20)
        ))
        
        # Search input
        self.search_input = TextInput(
            hint_text='Search students by name or matricule...',
            multiline=False,
            size_hint_x=0.6,
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT_PRIMARY,
            cursor_color=PRIMARY_COLOR,
            font_size=sp(14),
            padding=[dp(10), dp(12)]
        )
        self.add_widget(self.search_input)
        
        # Search button
        self.search_btn = ModernButton(
            text='Search',
            size_hint_x=0.2,
            button_color=PRIMARY_COLOR
        )
        if on_search:
            self.search_btn.bind(on_press=lambda x: on_search(self.search_input.text))
        self.add_widget(self.search_btn)
        
        # Clear button
        self.clear_btn = ModernButton(
            text='Clear',
            size_hint_x=0.15,
            button_color=TEXT_SECONDARY
        )
        if on_clear:
            self.clear_btn.bind(on_press=lambda x: self._clear())
        self.add_widget(self.clear_btn)
        
        self.on_search_callback = on_search
        self.on_clear_callback = on_clear
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def _clear(self):
        self.search_input.text = ''
        if self.on_clear_callback:
            self.on_clear_callback()

class LoadingPopup(Popup):
    """Modern loading indicator"""
    def __init__(self, title='Loading...', **kwargs):
        content = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        
        # Progress bar with modern styling
        self.progress = ProgressBar(max=100)
        
        # Custom progress bar colors
        with self.progress.canvas.before:
            Color(*BACKGROUND_DARK)
            self.progress_bg = RoundedRectangle(
                pos=self.progress.pos,
                size=self.progress.size,
                radius=[dp(8)]
            )
        
        self.label = ModernLabel(text='Please wait...', subtitle=True)
        
        content.add_widget(self.progress)
        content.add_widget(self.label)
        
        super().__init__(
            title=title,
            content=content,
            size_hint=(0.7, 0.3),
            auto_dismiss=False,
            background_color=(0, 0, 0, 0),
            **kwargs
        )
    
    def update_progress(self, value, message=''):
        self.progress.value = value * 100
        if message:
            self.label.text = message

class ConfirmationDialog(Popup):
    """Modern confirmation dialog"""
    def __init__(self, message, on_yes=None, on_no=None, **kwargs):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Icon
        icon_box = BoxLayout(size_hint_y=None, height=dp(60))
        icon = Label(
            text='⚠️',
            font_size=sp(40),
            size_hint_y=None,
            height=dp(60)
        )
        icon_box.add_widget(icon)
        content.add_widget(icon_box)
        
        # Message
        msg_label = ModernLabel(
            text=message,
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(msg_label)
        
        # Buttons
        btn_layout = BoxLayout(spacing=dp(15), size_hint_y=None, height=dp(50))
        
        no_btn = ModernButton(
            text='Cancel',
            button_color=TEXT_SECONDARY
        )
        yes_btn = ModernButton(
            text='Confirm',
            button_color=ERROR_COLOR
        )
        
        if on_yes:
            yes_btn.bind(on_press=lambda x: (on_yes(), self.dismiss()))
        else:
            yes_btn.bind(on_press=lambda x: self.dismiss())
        
        if on_no:
            no_btn.bind(on_press=lambda x: (on_no(), self.dismiss()))
        else:
            no_btn.bind(on_press=lambda x: self.dismiss())
        
        btn_layout.add_widget(no_btn)
        btn_layout.add_widget(yes_btn)
        
        content.add_widget(btn_layout)
        
        super().__init__(
            title='Confirmation Required',
            content=content,
            size_hint=(0.7, 0.5),
            **kwargs
        )

def show_error(message, title='Error'):
    """Show modern error popup"""
    content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
    
    # Error icon
    icon = Label(text='❌', font_size=sp(50), size_hint_y=None, height=dp(70))
    content.add_widget(icon)
    
    # Message
    msg = ModernLabel(text=message, size_hint_y=None, height=dp(100))
    content.add_widget(msg)
    
    # OK button
    ok_btn = ModernButton(
        text='OK',
        size_hint=(None, None),
        size=(dp(120), dp(45)),
        pos_hint={'center_x': 0.5},
        button_color=ERROR_COLOR
    )
    
    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.7, 0.5),
        auto_dismiss=False
    )
    
    ok_btn.bind(on_press=popup.dismiss)
    content.add_widget(ok_btn)
    
    popup.open()
    logger.error(f"{title}: {message}")

def show_success(message, title='Success'):
    """Show modern success popup"""
    content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
    
    # Success icon
    icon = Label(text='✅', font_size=sp(50), size_hint_y=None, height=dp(70))
    content.add_widget(icon)
    
    # Message
    msg = ModernLabel(text=message, size_hint_y=None, height=dp(100))
    content.add_widget(msg)
    
    # OK button
    ok_btn = ModernButton(
        text='OK',
        size_hint=(None, None),
        size=(dp(120), dp(45)),
        pos_hint={'center_x': 0.5},
        button_color=SUCCESS_COLOR
    )
    
    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.7, 0.5),
        auto_dismiss=False
    )
    
    ok_btn.bind(on_press=popup.dismiss)
    content.add_widget(ok_btn)
    
    popup.open()
    logger.info(f"{title}: {message}")

# ============================================
# MAIN SCREEN WITH MODERN GUI
# ============================================
class MainScreen(Screen):
    """Enhanced main screen with modern design"""
    
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.selected_groupe = None
        self.current_page = 1
        self.total_pages = 1
        self.search_mode = False
        self.search_results = []
        
        self.build_ui()
    
    def build_ui(self):
        """Build the modern user interface"""
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Beautiful gradient header
        header = GradientHeader(title_text=Config.APP_NAME)
        main_layout.add_widget(header)
        
        # Main content area with padding
        content_area = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15)
        )
        
        # Top controls card
        controls_card = ModernCard(size_hint_y=None, height=dp(70))
        controls_card.orientation = 'horizontal'
        controls_card.spacing = dp(10)
        
        # Group selector
        self.group_spinner = Spinner(
            text='Select Group',
            values=[],
            size_hint_x=0.25,
            background_color=PRIMARY_LIGHT,
            color=(1, 1, 1, 1),
            font_size=sp(14)
        )
        self.group_spinner.bind(text=self.on_group_selected)
        controls_card.add_widget(self.group_spinner)
        
        # Import button
        import_btn = ModernButton(
            text='📥 Import',
            size_hint_x=0.18,
            button_color=ACCENT_COLOR
        )
        import_btn.bind(on_press=self.open_file_chooser)
        controls_card.add_widget(import_btn)
        
        # Export button
        export_btn = ModernButton(
            text='📤 Export',
            size_hint_x=0.18,
            button_color=SUCCESS_COLOR
        )
        export_btn.bind(on_press=self.export_data)
        controls_card.add_widget(export_btn)
        
        # Backup button
        backup_btn = ModernButton(
            text='💾 Backup',
            size_hint_x=0.17,
            button_color=WARNING_COLOR
        )
        backup_btn.bind(on_press=self.backup_database)
        controls_card.add_widget(backup_btn)
        
        # Refresh button
        refresh_btn = ModernButton(
            text='🔄 Refresh',
            size_hint_x=0.17,
            button_color=INFO_COLOR
        )
        refresh_btn.bind(on_press=lambda x: self.refresh_data())
        controls_card.add_widget(refresh_btn)
        
        content_area.add_widget(controls_card)
        
        # Search bar
        self.search_bar = SearchBar(
            on_search=self.perform_search,
            on_clear=self.clear_search
        )
        content_area.add_widget(self.search_bar)
        
        # Student count label
        self.count_label = ModernLabel(
            text='Select a group to view students',
            subtitle=True,
            size_hint_y=None,
            height=dp(30)
        )
        content_area.add_widget(self.count_label)
        
        # Student list in a card
        list_card = ModernCard()
        list_card.orientation = 'vertical'
        list_card.spacing = 0
        list_card.padding = 0
        
        scroll = ScrollView()
        self.student_grid = GridLayout(
            cols=1,
            spacing=dp(2),
            size_hint_y=None,
            padding=dp(10)
        )
        self.student_grid.bind(minimum_height=self.student_grid.setter('height'))
        scroll.add_widget(self.student_grid)
        list_card.add_widget(scroll)
        
        content_area.add_widget(list_card)
        
        # Pagination controls
        pagination = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        self.prev_btn = ModernButton(
            text='◀ Previous',
            size_hint_x=0.25,
            disabled=True,
            button_color=TEXT_SECONDARY
        )
        self.prev_btn.bind(on_press=lambda x: self.change_page(-1))
        pagination.add_widget(self.prev_btn)
        
        self.page_label = ModernLabel(
            text='Page 1 of 1',
            subtitle=True,
            size_hint_x=0.5
        )
        pagination.add_widget(self.page_label)
        
        self.next_btn = ModernButton(
            text='Next ▶',
            size_hint_x=0.25,
            disabled=True,
            button_color=TEXT_SECONDARY
        )
        self.next_btn.bind(on_press=lambda x: self.change_page(1))
        pagination.add_widget(self.next_btn)
        
        content_area.add_widget(pagination)
        
        main_layout.add_widget(content_area)
        
        # Footer with developer info
        footer = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            padding=[dp(20), dp(5)]
        )
        footer_label = Label(
            text=f'© {Config.YEAR} {Config.DEVELOPER} - All Rights Reserved',
            font_size=sp(11),
            color=TEXT_SECONDARY
        )
        footer.add_widget(footer_label)
        main_layout.add_widget(footer)
        
        self.add_widget(main_layout)
        
        # Load groups on init
        Clock.schedule_once(lambda dt: self.refresh_groups(), 0.5)
    
    def refresh_groups(self):
        """Refresh the list of available groups"""
        groups = self.db.get_all_groups()
        if groups:
            self.group_spinner.values = groups
            logger.info(f"Loaded {len(groups)} groups")
        else:
            self.group_spinner.values = ['No groups available']
            logger.warning("No groups found in database")
    
    def on_group_selected(self, spinner, text):
        """Handle group selection"""
        if text and text != 'Select Group' and text != 'No groups available':
            self.selected_groupe = text
            self.current_page = 1
            self.search_mode = False
            self.search_bar.search_input.text = ''
            self.load_students()
    
    def load_students(self):
        """Load students for selected group with pagination"""
        if not self.selected_groupe:
            return
        
        students, page, total_pages, total_count = self.db.get_students_paginated(
            self.selected_groupe,
            self.current_page
        )
        
        self.total_pages = total_pages
        self.display_students(students, total_count)
        self.update_pagination_controls()
    
    def display_students(self, students, total_count=None):
        """Display student list with modern design"""
        self.student_grid.clear_widgets()
        
        if not students:
            empty_label = ModernLabel(
                text='No students found',
                subtitle=True,
                size_hint_y=None,
                height=dp(80)
            )
            self.student_grid.add_widget(empty_label)
            self.count_label.text = 'No students'
            return
        
        # Update count
        if total_count is not None:
            if self.search_mode:
                self.count_label.text = f'🔍 Found {len(students)} students'
            else:
                self.count_label.text = f'📊 Total: {total_count} students (Page {self.current_page}/{self.total_pages})'
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5), padding=[dp(5), 0])
        header.add_widget(ModernLabel(text='#', size_hint_x=0.08, bold=True))
        header.add_widget(ModernLabel(text='Matricule', size_hint_x=0.22, bold=True))
        header.add_widget(ModernLabel(text='Full Name', size_hint_x=0.35, bold=True))
        header.add_widget(ModernLabel(text='Section', size_hint_x=0.15, bold=True))
        header.add_widget(ModernLabel(text='Actions', size_hint_x=0.2, bold=True))
        self.student_grid.add_widget(header)
        
        # Student rows with alternating colors
        start_num = (self.current_page - 1) * Config.STUDENTS_PER_PAGE + 1
        for idx, student in enumerate(students):
            row = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5), padding=[dp(5), dp(3)])
            
            # Alternating row colors
            bg_color = BACKGROUND_DARK if idx % 2 == 0 else CARD_COLOR
            with row.canvas.before:
                Color(*bg_color)
                row.rect = RoundedRectangle(
                    pos=row.pos,
                    size=row.size,
                    radius=[dp(6)]
                )
            row.bind(size=lambda obj, val: setattr(obj.rect, 'size', val))
            row.bind(pos=lambda obj, val: setattr(obj.rect, 'pos', val))
            
            # Row number
            row.add_widget(ModernLabel(text=str(start_num + idx), size_hint_x=0.08))
            
            # Matricule
            row.add_widget(ModernLabel(text=student[1], size_hint_x=0.22))
            
            # Full name
            full_name = f"{student[3]} {student[2]}"
            row.add_widget(ModernLabel(text=full_name, size_hint_x=0.35))
            
            # Section
            section = student[4] if student[4] else 'N/A'
            row.add_widget(ModernLabel(text=section, size_hint_x=0.15))
            
            # Actions
            actions = BoxLayout(size_hint_x=0.2, spacing=dp(5))
            
            view_btn = ModernButton(
                text='👁',
                size_hint_x=0.5,
                button_color=INFO_COLOR
            )
            view_btn.bind(on_press=lambda x, s=student: self.view_student_details(s))
            actions.add_widget(view_btn)
            
            delete_btn = ModernButton(
                text='🗑',
                size_hint_x=0.5,
                button_color=ERROR_COLOR
            )
            delete_btn.bind(on_press=lambda x, s=student: self.confirm_delete_student(s))
            actions.add_widget(delete_btn)
            
            row.add_widget(actions)
            
            self.student_grid.add_widget(row)
    
    def update_pagination_controls(self):
        """Update pagination button states"""
        self.page_label.text = f'Page {self.current_page} of {self.total_pages}'
        
        self.prev_btn.disabled = (self.current_page <= 1)
        self.next_btn.disabled = (self.current_page >= self.total_pages)
        
        # Update button colors based on state
        if self.prev_btn.disabled:
            self.prev_btn.button_color = DISABLED_COLOR
        else:
            self.prev_btn.button_color = PRIMARY_COLOR
        
        if self.next_btn.disabled:
            self.next_btn.button_color = DISABLED_COLOR
        else:
            self.next_btn.button_color = PRIMARY_COLOR
    
    def change_page(self, direction):
        """Change current page"""
        new_page = self.current_page + direction
        
        if 1 <= new_page <= self.total_pages:
            self.current_page = new_page
            self.load_students()
    
    def perform_search(self, query):
        """Perform student search"""
        if not query or not query.strip():
            show_error("Please enter a search term")
            return
        
        self.search_mode = True
        self.search_results = self.db.search_students(query, self.selected_groupe)
        
        self.display_students(self.search_results)
        
        # Disable pagination in search mode
        self.prev_btn.disabled = True
        self.next_btn.disabled = True
        self.page_label.text = 'Search Results'
    
    def clear_search(self):
        """Clear search and return to normal view"""
        self.search_mode = False
        self.search_results = []
        self.current_page = 1
        
        if self.selected_groupe:
            self.load_students()
        else:
            self.student_grid.clear_widgets()
            self.count_label.text = 'Select a group'
    
    def view_student_details(self, student):
        """Show detailed student information in modern popup"""
        stats = self.db.get_student_stats(student[0])
        
        if not stats:
            show_error("Could not load student details")
            return
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Student icon
        icon = Label(text='👨‍🎓', font_size=sp(60), size_hint_y=None, height=dp(80))
        content.add_widget(icon)
        
        # Info card
        info_card = ModernCard()
        info_card.orientation = 'vertical'
        info_card.size_hint_y = None
        info_card.height = dp(280)
        
        details_text = f"""[b]{student[3]} {student[2]}[/b]

📋 Matricule: {student[1]}
📚 Section: {student[4] or 'N/A'}
👥 Group: {student[5]}

📊 Academic Performance:
   • Average Score: {stats['avg_score']}/20
   • Best Score: {stats['max_score']}/20
   • Worst Score: {stats['min_score']}/20
   • Total Exams: {stats['total_marks']}

📅 Attendance:
   • Total Classes: {stats['total_classes']}
   • Present: {stats['present_count']}
   • Attendance Rate: {stats['attendance_rate']}%
"""
        
        details_label = Label(
            text=details_text,
            markup=True,
            color=TEXT_PRIMARY,
            font_size=sp(13),
            halign='left',
            valign='top'
        )
        details_label.bind(size=details_label.setter('text_size'))
        info_card.add_widget(details_label)
        
        content.add_widget(info_card)
        
        # Close button
        close_btn = ModernButton(
            text='Close',
            size_hint=(None, None),
            size=(dp(150), dp(45)),
            pos_hint={'center_x': 0.5},
            button_color=PRIMARY_COLOR
        )
        
        popup = Popup(
            title='Student Details',
            content=content,
            size_hint=(0.8, 0.8)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def confirm_delete_student(self, student):
        """Show confirmation before deleting student"""
        message = f"Are you sure you want to delete:\n\n{student[3]} {student[2]}\nMatricule: {student[1]}\n\nThis will delete all related records!"
        
        ConfirmationDialog(
            message=message,
            on_yes=lambda: self.delete_student(student[0])
        ).open()
    
    def delete_student(self, student_id):
        """Delete a student"""
        success, message = self.db.delete_student(student_id)
        
        if success:
            show_success(message)
            self.refresh_data()
        else:
            show_error(message)
    
    def open_file_chooser(self, instance):
        """Open file chooser for Excel import"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Group name input card
        group_card = ModernCard(size_hint_y=None, height=dp(70))
        group_layout = BoxLayout(spacing=dp(10))
        group_layout.add_widget(ModernLabel(
            text='Group Name (optional):',
            size_hint_x=0.4
        ))
        group_input = TextInput(
            hint_text='e.g., Groupe10',
            size_hint_x=0.6,
            multiline=False,
            background_color=(0.95, 0.95, 0.96, 1),
            foreground_color=TEXT_PRIMARY,
            font_size=sp(14),
            padding=[dp(10), dp(12)]
        )
        group_layout.add_widget(group_input)
        group_card.add_widget(group_layout)
        content.add_widget(group_card)
        
        # File chooser
        file_chooser = FileChooserListView(
            filters=['*.xlsx', '*.xls'],
            size_hint_y=0.75
        )
        content.add_widget(file_chooser)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10))
        
        def do_import(instance):
            if file_chooser.selection:
                file_path = file_chooser.selection[0]
                groupe_name = group_input.text.strip() or None
                
                popup.dismiss()
                self.import_excel(file_path, groupe_name)
        
        import_btn = ModernButton(
            text='Import',
            button_color=SUCCESS_COLOR
        )
        import_btn.bind(on_press=do_import)
        btn_layout.add_widget(import_btn)
        
        cancel_btn = ModernButton(
            text='Cancel',
            button_color=ERROR_COLOR
        )
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Import Excel File',
            content=content,
            size_hint=(0.9, 0.9)
        )
        popup.open()
    
    def import_excel(self, file_path, groupe_name):
        """Import Excel file with progress indicator"""
        loading = LoadingPopup(title='Importing Students...')
        loading.open()
        
        def update_progress(value):
            loading.update_progress(value, f'Importing... {int(value * 100)}%')
        
        def do_import():
            success, message, count = self.db.import_from_excel(
                file_path,
                groupe_name,
                progress_callback=update_progress
            )
            
            Clock.schedule_once(lambda dt: self._import_complete(loading, success, message), 0)
        
        thread = threading.Thread(target=do_import)
        thread.start()
    
    def _import_complete(self, loading_popup, success, message):
        """Handle import completion"""
        loading_popup.dismiss()
        
        if success:
            show_success(message, 'Import Successful')
            self.refresh_groups()
            self.refresh_data()
        else:
            show_error(message, 'Import Failed')
    
    def export_data(self, instance):
        """Export current data to Excel"""
        if not self.selected_groupe:
            show_error("Please select a group first")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"export_{self.selected_groupe}_{timestamp}.xlsx"
        output_path = os.path.join('exports', filename)
        
        os.makedirs('exports', exist_ok=True)
        
        success, message = self.db.export_to_excel(output_path, self.selected_groupe)
        
        if success:
            show_success(message, 'Export Successful')
        else:
            show_error(message, 'Export Failed')
    
    def backup_database(self, instance):
        """Create database backup"""
        success, result = self.db.backup_database()
        
        if success:
            show_success(f"Database backed up successfully!\n\n{result}", 'Backup Complete')
        else:
            show_error(result, 'Backup Failed')
    
    def refresh_data(self):
        """Refresh current view"""
        if self.search_mode:
            self.clear_search()
        elif self.selected_groupe:
            self.load_students()

# ============================================
# APPLICATION
# ============================================
class StudentTrackerApp(App):
    """Enhanced Kivy application with modern GUI"""
    
    def build(self):
        self.title = f'{Config.APP_NAME} - by {Config.DEVELOPER}'
        self.db = StudentTrackerDB()
        
        # Set window properties
        Window.size = (1280, 820)
        Window.minimum_width = 1000
        Window.minimum_height = 700
        Window.clearcolor = BACKGROUND_COLOR
        
        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main', db=self.db))
        
        # Schedule auto-backup
        Clock.schedule_interval(
            lambda dt: self.auto_backup(),
            Config.AUTO_BACKUP_INTERVAL
        )
        
        logger.info(f"Application started successfully - {Config.APP_NAME} by {Config.DEVELOPER}")
        return sm
    
    def auto_backup(self):
        """Perform automatic database backup"""
        success, result = self.db.backup_database()
        if success:
            logger.info(f"Auto-backup completed: {result}")
        else:
            logger.error(f"Auto-backup failed: {result}")
    
    def on_stop(self):
        """Cleanup when app closes"""
        logger.info("Application closing")
        self.db.backup_database()

if __name__ == '__main__':
    StudentTrackerApp().run()
