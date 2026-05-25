def calculate_clock_angle(hours, minutes, seconds):

    s_angle = seconds * 6
    
    m_angle = (minutes * 6) - (seconds * (6 / 60))
    
    h_angle = (hours % 12 * 30) + (minutes * 0.5) + (seconds * (0.5 / 60))
    
    angle = abs(h_angle - m_angle)
    
    return min(angle, 360 + angle)

print(f"Angle: {calculate_clock_angle(5, 30, 30)}°")