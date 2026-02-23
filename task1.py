"""
Модуль для розрахунку кутів між стрілками аналогового годинника.
Забезпечує точність з урахуванням руху секундної стрілки.
"""

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def get_clock_angle(hours, minutes, seconds):
    """
    Обчислює найменший кут між годинною та хвилинною стрілками.

    Args:
        hours (int): Години (0-23).
        minutes (int): Хвилини (0-59).
        seconds (int): Секунди (0-59).

    Returns:
        float: Кут у градусах (від 0 до 180).
    """
    # Переводимо у 12-годинний формат
    h = hours % 12
    
    # Позиція годинної стрілки: 30 градусів на годину + зміщення від хвилин і секунд
    # 0.5 градуса за хвилину, 0.5/60 градуса за секунду 
    h_pos = (h * 30) + (minutes * 0.5) + (seconds * (0.5 / 60))
    
    # Позиція хвилинної стрілки: 6 градусів за хвилину + зміщення від секунд
    # 0.1 градуса за секунду 
    m_pos = (minutes * 6) + (seconds * 0.1)
    
    # Знаходимо різницю
    angle = abs(h_pos - m_pos)
    
    # Повертаємо найменший кут
    return min(angle, 360 - angle)

if __name__ == "__main__":
    h, m, s = 10, 10, 30
    angle = get_clock_angle(h, m, s)
    logger.info(f"Час {h:02d}:{m:02d}:{s:02d}. Кут між стрілками: {angle:.2f} градусів.")