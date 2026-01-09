import pandas as pd
from io import BytesIO


def generate_template():
    """generates excel template with sample data"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # 1. departments
        df_dept = pd.DataFrame({
            'kod': ['WI', 'WE', 'WM', 'WZ'],
            'nazwa': ['Wydział Informatyki', 'Wydział Elektroniki', 'Wydział Mechaniczny', 'Wydział Zarządzania']
        })
        df_dept.to_excel(writer, sheet_name='Wydzialy', index=False)
        
        # 2. buildings
        df_buildings = pd.DataFrame({
            'nazwa': ['Budynek A', 'Budynek B', 'Budynek C', 'Budynek D', 'Budynek E'],
            'adres': ['ul. Akademicka 1', 'ul. Akademicka 2', 'ul. Techniczna 5', 'ul. Naukowa 10', 'ul. Studencka 3'],
            'kod_wydzialu': ['WI', 'WI', 'WE', 'WM', 'WZ']
        })
        df_buildings.to_excel(writer, sheet_name='Budynki', index=False)
        
        # 3. rooms
        rooms_data = []
        
        # Building A - Informatics
        rooms_data.extend([
            ['A101', 'Sala wykładowa duża', 'Budynek A', 120, 'lecture_hall', 'Projektor, nagłośnienie'],
            ['A102', 'Sala wykładowa mała', 'Budynek A', 60, 'lecture_hall', 'Projektor'],
            ['A103', 'Laboratorium programowania 1', 'Budynek A', 30, 'computer_lab', '30 komputerów'],
            ['A104', 'Laboratorium programowania 2', 'Budynek A', 30, 'computer_lab', '30 komputerów'],
            ['A105', 'Laboratorium sieci', 'Budynek A', 28, 'computer_lab', 'Routery, switche'],
            ['A106', 'Laboratorium programowania 3', 'Budynek A', 32, 'computer_lab', '32 komputery'],
            ['A107', 'DUŻE Laboratorium 1', 'Budynek A', 50, 'computer_lab', '50 komputerów'],
            ['A201', 'Laboratorium AI/ML', 'Budynek A', 25, 'computer_lab', 'GPU workstations'],
            ['A202', 'Laboratorium baz danych', 'Budynek A', 30, 'computer_lab', 'Serwery SQL'],
            ['A203', 'Sala ćwiczeniowa', 'Budynek A', 50, 'classroom', 'Duża sala'],
            ['A204', 'Sala ćwiczeniowa', 'Budynek A', 52, 'classroom', 'Duża sala'],
            ['A205', 'DUŻA Sala ćwiczeniowa', 'Budynek A', 60, 'classroom', 'Bardzo duża'],
            ['A206', 'NAJWIĘKSZA Sala', 'Budynek A', 65, 'classroom', 'Największa'],
        ])
        
        # Building B - Informatics 
        rooms_data.extend([
            ['B101', 'Audytorium A', 'Budynek B', 200, 'auditorium', 'Scena, projektor'],
            ['B102', 'Sala konferencyjna', 'Budynek B', 80, 'seminar_room', 'Sprzęt konferencyjny'],
            ['B103', 'Sala seminaryjna 1', 'Budynek B', 35, 'seminar_room', ''],
            ['B104', 'Sala seminaryjna 2', 'Budynek B', 35, 'seminar_room', ''],
            ['B105', 'Sala seminaryjna 3', 'Budynek B', 40, 'seminar_room', ''],
            ['B106', 'Warsztat elektroniki', 'Budynek B', 25, 'workshop', 'Stacje lutownicze, zestawy'],
            ['B107', 'Sala projektowa', 'Budynek B', 30, 'workshop', 'Stoliki projektowe'],
            ['B201', 'Sala wykładowa', 'Budynek B', 110, 'lecture_hall', 'Projektor'],
            ['B202', 'Sala ćwiczeniowa', 'Budynek B', 45, 'classroom', ''],
            ['B203', 'Sala ćwiczeniowa', 'Budynek B', 48, 'classroom', ''],
            ['B204', 'Sala ćwiczeniowa', 'Budynek B', 45, 'classroom', ''],
            ['B205', 'Sala ćwiczeniowa', 'Budynek B', 50, 'classroom', ''],
            ['B206', 'Sala ćwiczeniowa mała', 'Budynek B', 30, 'classroom', ''],
            ['B207', 'Sala ćwiczeniowa mała', 'Budynek B', 32, 'classroom', ''],
            ['B208', 'Sala gimnastyczna', 'Budynek B', 80, 'gym', 'Mata, sprzęt fitness, piłki'],
        ])
        
        # Building C - Electronics
        rooms_data.extend([
            ['C101', 'Sala wykładowa', 'Budynek C', 100, 'lecture_hall', ''],
            ['C102', 'Lab. elektroniki 1', 'Budynek C', 25, 'physics_lab', 'Oscyloskopy'],
            ['C103', 'Lab. elektroniki 2', 'Budynek C', 25, 'physics_lab', 'Oscyloskopy'],
            ['C104', 'Lab. pomiarów', 'Budynek C', 25, 'physics_lab', 'Multimetry'],
            ['C105', 'Lab. mikroprocesorów', 'Budynek C', 26, 'computer_lab', 'Zestawy Arduino'],
            ['C106', 'Lab. automatyki', 'Budynek C', 28, 'physics_lab', 'PLC'],
            ['C201', 'Sala ćwiczeniowa', 'Budynek C', 40, 'classroom', ''],
            ['C202', 'Sala ćwiczeniowa', 'Budynek C', 42, 'classroom', ''],
            ['C203', 'Sala seminaryjna', 'Budynek C', 30, 'seminar_room', ''],
            ['C204', 'Sala projektowa', 'Budynek C', 35, 'workshop', 'Stanowiska projektowe'],
            ['C205', 'Warsztat elektroniczny', 'Budynek C', 20, 'workshop', 'Stacje lutownicze'],
            ['C301', 'Lab. cyfrowych układów', 'Budynek C', 22, 'physics_lab', ''],
            ['C302', 'Lab. telekomunikacji', 'Budynek C', 25, 'physics_lab', ''],
            ['C303', 'Lab. antenowe', 'Budynek C', 18, 'physics_lab', ''],
            ['C304', 'Sala wykładowa duża', 'Budynek C', 110, 'lecture_hall', ''],
        ])
        
        # Building D - Mechanical
        rooms_data.extend([
            ['D101', 'Sala wykładowa', 'Budynek D', 110, 'lecture_hall', ''],
            ['D102', 'Lab. mechaniki', 'Budynek D', 20, 'physics_lab', 'Stanowiska pomiarowe'],
            ['D103', 'Lab. wytrzymałości', 'Budynek D', 25, 'physics_lab', 'Maszyna wytrzymałościowa'],
            ['D104', 'Warsztat mechaniczny', 'Budynek D', 16, 'workshop', 'Tokarki, frezarki'],
            ['D105', 'Lab. CAD/CAM', 'Budynek D', 30, 'computer_lab', 'Oprogramowanie CAD'],
            ['D201', 'Sala ćwiczeniowa', 'Budynek D', 45, 'classroom', ''],
            ['D202', 'Sala projektowa', 'Budynek D', 30, 'workshop', 'Stoliki projektowe'],
            ['D203', 'Lab. robotyki', 'Budynek D', 22, 'workshop', 'Roboty przemysłowe'],
            ['D204', 'Sala seminaryjna', 'Budynek D', 28, 'seminar_room', ''],
            ['D205', 'Lab. termodynamiki', 'Budynek D', 20, 'physics_lab', ''],
        ])
        
        # Building E - Management
        rooms_data.extend([
            ['E101', 'Sala wykładowa', 'Budynek E', 95, 'lecture_hall', ''],
            ['E102', 'Sala konferencyjna', 'Budynek E', 50, 'seminar_room', 'Duży stół konferencyjny'],
            ['E103', 'Sala ćwiczeniowa', 'Budynek E', 40, 'classroom', ''],
            ['E104', 'Lab. językowe', 'Budynek E', 24, 'language_lab', 'Stanowiska językowe'],
            ['E105', 'Sala gimnastyczna duża', 'Budynek E', 100, 'gym', 'Sprzęt sportowy, boisko'],
            ['E106', 'Sala gimnastyczna mała', 'Budynek E', 35, 'gym', 'Mata, sprzęt fitness'],
        ])
        
        df_rooms = pd.DataFrame(rooms_data, columns=['kod', 'nazwa', 'nazwa_budynku', 'pojemnosc', 'typ', 'notatki'])
        df_rooms.to_excel(writer, sheet_name='Sale', index=False)
        
        # 4. groups
        groups_data = [
            ['1WI-INF', 'Informatyka rok 1', 'WI', 120, ''],
            ['1WI-INF-L1', 'Informatyka rok 1 - Lab 1', 'WI', 30, '1WI-INF'],
            ['1WI-INF-L2', 'Informatyka rok 1 - Lab 2', 'WI', 30, '1WI-INF'],
            ['1WI-INF-L3', 'Informatyka rok 1 - Lab 3', 'WI', 30, '1WI-INF'],
            ['1WI-INF-L4', 'Informatyka rok 1 - Lab 4', 'WI', 30, '1WI-INF'],
            ['2WI-INF', 'Informatyka rok 2', 'WI', 110, ''],
            ['2WI-INF-L1', 'Informatyka rok 2 - Lab 1', 'WI', 28, '2WI-INF'],
            ['2WI-INF-L2', 'Informatyka rok 2 - Lab 2', 'WI', 27, '2WI-INF'],
            ['2WI-INF-L3', 'Informatyka rok 2 - Lab 3', 'WI', 28, '2WI-INF'],
            ['2WI-INF-L4', 'Informatyka rok 2 - Lab 4', 'WI', 27, '2WI-INF'],
            
            ['1WE-ELE', 'Elektronika rok 1', 'WE', 100, ''],
            ['1WE-ELE-L1', 'Elektronika rok 1 - Lab 1', 'WE', 25, '1WE-ELE'],
            ['1WE-ELE-L2', 'Elektronika rok 1 - Lab 2', 'WE', 25, '1WE-ELE'],
            ['1WE-ELE-L3', 'Elektronika rok 1 - Lab 3', 'WE', 25, '1WE-ELE'],
            ['1WE-ELE-L4', 'Elektronika rok 1 - Lab 4', 'WE', 25, '1WE-ELE'],
            
            ['1WM-MEC', 'Mechanika rok 1', 'WM', 90, ''],
            ['1WM-MEC-L1', 'Mechanika rok 1 - Lab 1', 'WM', 22, '1WM-MEC'],
            ['1WM-MEC-L2', 'Mechanika rok 1 - Lab 2', 'WM', 23, '1WM-MEC'],
            ['1WM-MEC-L3', 'Mechanika rok 1 - Lab 3', 'WM', 22, '1WM-MEC'],
            ['1WM-MEC-L4', 'Mechanika rok 1 - Lab 4', 'WM', 23, '1WM-MEC'],
            
            ['1WZ-ZAR', 'Zarządzanie rok 1', 'WZ', 80, ''],
            ['1WZ-ZAR-C1', 'Zarządzanie rok 1 - Ćw 1', 'WZ', 40, '1WZ-ZAR'],
            ['1WZ-ZAR-C2', 'Zarządzanie rok 1 - Ćw 2', 'WZ', 40, '1WZ-ZAR'],
            ['1WZ-ZAR-J1', 'Zarządzanie rok 1 - Język 1', 'WZ', 24, '1WZ-ZAR'],
            ['1WZ-ZAR-J2', 'Zarządzanie rok 1 - Język 2', 'WZ', 24, '1WZ-ZAR'],
        ]
        
        df_groups = pd.DataFrame(groups_data, columns=['kod', 'nazwa', 'kod_wydzialu', 'liczba_studentow', 'parent_kod'])
        df_groups.to_excel(writer, sheet_name='Grupy', index=False)
        
        # 5. teachers
        teachers_data = [
            ['Jan', 'Kowalski', 'WI'],
            ['Anna', 'Nowak', 'WI'],
            ['Piotr', 'Wiśniewski', 'WI'],
            ['Maria', 'Wójcik', 'WI'],
            ['Tomasz', 'Kamiński', 'WI'],
            ['Katarzyna', 'Lewandowska', 'WI'],
            ['Michał', 'Zieliński', 'WI'],
            ['Agnieszka', 'Szymańska', 'WI'],
            
            ['Marek', 'Woźniak', 'WE'],
            ['Ewa', 'Dąbrowska', 'WE'],
            ['Paweł', 'Kozłowski', 'WE'],
            ['Magdalena', 'Jankowska', 'WE'],
            ['Krzysztof', 'Mazur', 'WE'],
            ['Joanna', 'Kwiatkowska', 'WE'],
            
            ['Andrzej', 'Krawczyk', 'WM'],
            ['Barbara', 'Piotrowski', 'WM'],
            ['Grzegorz', 'Grabowski', 'WM'],
            ['Monika', 'Pawłowska', 'WM'],
            ['Jacek', 'Michalski', 'WM'],
            
            ['Elżbieta', 'Adamczyk', 'WZ'],
            ['Robert', 'Dudek', 'WZ'],
            ['Teresa', 'Nowakowski', 'WZ'],
            ['Stanisław', 'Król', 'WZ'],
        ]
        
        df_teachers = pd.DataFrame(teachers_data, columns=['imie', 'nazwisko', 'kod_wydzialu'])
        df_teachers.to_excel(writer, sheet_name='Prowadzacy', index=False)
        
        # 6. courses
        courses_data = [
            # Informatics
            ['INF-PROG1', 'Programowanie 1', 'WI', 'lecture', 30],
            ['INF-PROG1-LAB', 'Programowanie 1 - Lab', 'WI', 'computer_lab', 30],
            ['INF-MAT', 'Matematyka dyskretna', 'WI', 'lecture', 30],
            ['INF-MAT-EX', 'Matematyka dyskretna - Ćw', 'WI', 'exercise', 30],
            ['INF-ALGO', 'Algorytmy i struktury danych', 'WI', 'lecture', 30],
            ['INF-ALGO-LAB', 'Algorytmy i struktury danych - Lab', 'WI', 'computer_lab', 30],
            ['INF-BD', 'Bazy danych', 'WI', 'lecture', 30],
            ['INF-BD-LAB', 'Bazy danych - Lab', 'WI', 'computer_lab', 30],
            ['INF-SIECI', 'Sieci komputerowe', 'WI', 'lecture', 30],
            ['INF-SIECI-LAB', 'Sieci komputerowe - Lab', 'WI', 'computer_lab', 30],
            ['INF-AI', 'Sztuczna inteligencja', 'WI', 'lecture', 30],
            ['INF-AI-LAB', 'Sztuczna inteligencja - Lab', 'WI', 'computer_lab', 30],
            ['INF-PROJ', 'Projekt zespołowy', 'WI', 'project', 30],
            
            # Electronics
            ['ELE-FIZ', 'Fizyka', 'WE', 'lecture', 30],
            ['ELE-FIZ-LAB', 'Fizyka - Lab', 'WE', 'physics_lab', 30],
            ['ELE-ELEK', 'Elektronika analogowa', 'WE', 'lecture', 30],
            ['ELE-ELEK-LAB', 'Elektronika analogowa - Lab', 'WE', 'physics_lab', 30],
            ['ELE-CYF', 'Układy cyfrowe', 'WE', 'lecture', 30],
            ['ELE-CYF-LAB', 'Układy cyfrowe - Lab', 'WE', 'physics_lab', 30],
            ['ELE-MIKRO', 'Mikroprocesory', 'WE', 'lecture', 30],
            ['ELE-MIKRO-LAB', 'Mikroprocesory - Lab', 'WE', 'computer_lab', 30],
            ['ELE-AUTO', 'Automatyka', 'WE', 'lecture', 30],
            ['ELE-AUTO-LAB', 'Automatyka - Lab', 'WE', 'physics_lab', 30],
            ['ELE-PROJ', 'Projekt elektroniczny', 'WE', 'workshop', 30],
            
            # Mechanika
            ['MEC-MECH', 'Mechanika techniczna', 'WM', 'lecture', 30],
            ['MEC-MECH-EX', 'Mechanika techniczna - Ćw', 'WM', 'exercise', 30],
            ['MEC-WYT', 'Wytrzymałość materiałów', 'WM', 'lecture', 30],
            ['MEC-WYT-LAB', 'Wytrzymałość materiałów - Lab', 'WM', 'physics_lab', 30],
            ['MEC-CAD', 'Projektowanie CAD', 'WM', 'lecture', 30],
            ['MEC-CAD-LAB', 'Projektowanie CAD - Lab', 'WM', 'computer_lab', 30],
            ['MEC-ROBOT', 'Robotyka', 'WM', 'lecture', 30],
            ['MEC-ROBOT-LAB', 'Robotyka - Lab', 'WM', 'workshop', 30],
            ['MEC-TERMO', 'Termodynamika', 'WM', 'lecture', 30],
            ['MEC-TERMO-LAB', 'Termodynamika - Lab', 'WM', 'physics_lab', 30],
            
            # Management
            ['ZAR-EKON', 'Ekonomia', 'WZ', 'lecture', 30],
            ['ZAR-EKON-EX', 'Ekonomia - Ćwiczenia', 'WZ', 'exercise', 30],
            ['ZAR-MARK', 'Marketing', 'WZ', 'lecture', 30],
            ['ZAR-MARK-SEM', 'Marketing - Seminarium', 'WZ', 'seminar', 30],
            ['ZAR-LANG', 'Język angielski biznesowy', 'WZ', 'language_lab', 30],
            ['ZAR-WF', 'Wychowanie fizyczne', 'WZ', 'gym_class', 30],
        ]
        
        df_courses = pd.DataFrame(courses_data, columns=['kod', 'nazwa', 'kod_wydzialu', 'typ', 'godziny_semestr'])
        df_courses.to_excel(writer, sheet_name='Przedmioty', index=False)
        
        # 7. course assignments
        assignments_data = [
            # Informatics year 1
            ['INF-PROG1', '1WI-INF', 'Jan Kowalski', '2024Z'],
            ['INF-PROG1-LAB', '1WI-INF-L1', 'Anna Nowak', '2024Z'],
            ['INF-PROG1-LAB', '1WI-INF-L2', 'Piotr Wiśniewski', '2024Z'],
            ['INF-PROG1-LAB', '1WI-INF-L3', 'Maria Wójcik', '2024Z'],
            ['INF-PROG1-LAB', '1WI-INF-L4', 'Tomasz Kamiński', '2024Z'],
            ['INF-MAT', '1WI-INF', 'Katarzyna Lewandowska', '2024Z'],
            ['INF-MAT-EX', '1WI-INF-L1', 'Michał Zieliński', '2024Z'],
            ['INF-MAT-EX', '1WI-INF-L2', 'Agnieszka Szymańska', '2024Z'],
            
            # Informatics year 2
            ['INF-ALGO', '2WI-INF', 'Jan Kowalski', '2024Z'],
            ['INF-ALGO-LAB', '2WI-INF-L1', 'Anna Nowak', '2024Z'],
            ['INF-ALGO-LAB', '2WI-INF-L2', 'Piotr Wiśniewski', '2024Z'],
            ['INF-BD', '2WI-INF', 'Maria Wójcik', '2024Z'],
            ['INF-BD-LAB', '2WI-INF-L1', 'Tomasz Kamiński', '2024Z'],
            ['INF-BD-LAB', '2WI-INF-L2', 'Katarzyna Lewandowska', '2024Z'],
            ['INF-SIECI', '2WI-INF', 'Michał Zieliński', '2024Z'],
            ['INF-SIECI-LAB', '2WI-INF-L1', 'Agnieszka Szymańska', '2024Z'],
            ['INF-AI', '2WI-INF', 'Jan Kowalski', '2024Z'],
            ['INF-AI-LAB', '2WI-INF-L1', 'Anna Nowak', '2024Z'],
            ['INF-PROJ', '2WI-INF-L1', 'Piotr Wiśniewski', '2024Z'],
            
            # Electronics
            ['ELE-FIZ', '1WE-ELE', 'Marek Woźniak', '2024Z'],
            ['ELE-FIZ-LAB', '1WE-ELE-L1', 'Ewa Dąbrowska', '2024Z'],
            ['ELE-FIZ-LAB', '1WE-ELE-L2', 'Paweł Kozłowski', '2024Z'],
            ['ELE-ELEK', '1WE-ELE', 'Magdalena Jankowska', '2024Z'],
            ['ELE-ELEK-LAB', '1WE-ELE-L1', 'Krzysztof Mazur', '2024Z'],
            ['ELE-ELEK-LAB', '1WE-ELE-L2', 'Joanna Kwiatkowska', '2024Z'],
            ['ELE-CYF', '1WE-ELE', 'Marek Woźniak', '2024Z'],
            ['ELE-CYF-LAB', '1WE-ELE-L1', 'Ewa Dąbrowska', '2024Z'],
            ['ELE-MIKRO', '1WE-ELE', 'Paweł Kozłowski', '2024Z'],
            ['ELE-MIKRO-LAB', '1WE-ELE-L1', 'Magdalena Jankowska', '2024Z'],
            ['ELE-AUTO', '1WE-ELE', 'Krzysztof Mazur', '2024Z'],
            ['ELE-AUTO-LAB', '1WE-ELE-L1', 'Joanna Kwiatkowska', '2024Z'],
            ['ELE-PROJ', '1WE-ELE-L1', 'Marek Woźniak', '2024Z'],
            
            # Mechanics
            ['MEC-MECH', '1WM-MEC', 'Andrzej Krawczyk', '2024Z'],
            ['MEC-MECH-EX', '1WM-MEC-L1', 'Barbara Piotrowski', '2024Z'],
            ['MEC-MECH-EX', '1WM-MEC-L2', 'Grzegorz Grabowski', '2024Z'],
            ['MEC-WYT', '1WM-MEC', 'Monika Pawłowska', '2024Z'],
            ['MEC-WYT-LAB', '1WM-MEC-L1', 'Jacek Michalski', '2024Z'],
            ['MEC-WYT-LAB', '1WM-MEC-L2', 'Andrzej Krawczyk', '2024Z'],
            ['MEC-CAD', '1WM-MEC', 'Barbara Piotrowski', '2024Z'],
            ['MEC-CAD-LAB', '1WM-MEC-L1', 'Grzegorz Grabowski', '2024Z'],
            ['MEC-ROBOT', '1WM-MEC', 'Monika Pawłowska', '2024Z'],
            ['MEC-ROBOT-LAB', '1WM-MEC-L1', 'Jacek Michalski', '2024Z'],
            ['MEC-TERMO', '1WM-MEC', 'Andrzej Krawczyk', '2024Z'],
            ['MEC-TERMO-LAB', '1WM-MEC-L1', 'Barbara Piotrowski', '2024Z'],
            
            # Management
            ['ZAR-EKON', '1WZ-ZAR', 'Elżbieta Adamczyk', '2024Z'],
            ['ZAR-EKON-EX', '1WZ-ZAR-C1', 'Robert Dudek', '2024Z'],
            ['ZAR-EKON-EX', '1WZ-ZAR-C2', 'Teresa Nowakowski', '2024Z'],
            ['ZAR-MARK', '1WZ-ZAR', 'Stanisław Król', '2024Z'],
            ['ZAR-MARK-SEM', '1WZ-ZAR-C1', 'Elżbieta Adamczyk', '2024Z'],
            ['ZAR-LANG', '1WZ-ZAR-J1', 'Robert Dudek', '2024Z'],
            ['ZAR-LANG', '1WZ-ZAR-J2', 'Teresa Nowakowski', '2024Z'],
            ['ZAR-WF', '1WZ-ZAR', 'Stanisław Król', '2024Z'],
        ]
        
        df_assignments = pd.DataFrame(assignments_data, columns=['kod_przedmiotu', 'kod_grupy', 'prowadzacy', 'semestr'])
        df_assignments.to_excel(writer, sheet_name='Przypisania', index=False)
    
    output.seek(0)
    return output



def generate_empty_template():
    """generate empty excel template - only headers + 1 sample row"""
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # manual
        df = pd.DataFrame({
            'Instrukcja wypełniania szablonu': [
                '1. Wypełnij kolejno wszystkie arkusze',
                '2. Zachowaj nazwy kolumn',
                '3. Używaj tylko dozwolonych typów',
                '4. parent_kod - kod grupy nadrzędnej (opcjonalnie)',
                '',
                'TYPY SAL:',
                'lecture_hall, classroom, auditorium,',
                'computer_lab, chemistry_lab, physics_lab,',
                'biology_lab, language_lab, seminar_room,',
                'workshop, gym, other',
                '',
                'TYPY PRZEDMIOTÓW:',
                'lecture, exercise, seminar, project,',
                'computer_lab, chemistry_lab, physics_lab,',
                'biology_lab, language_lab, workshop,',
                'gym_class, other'
            ]
        })
        df.to_excel(writer, sheet_name='Instrukcja', index=False)
        
        # 1. departments
        df = pd.DataFrame({
            'kod': ['WI'],
            'nazwa': ['Wydział Informatyki']
        })
        df.to_excel(writer, sheet_name='Wydzialy', index=False)
        
        # 2. buildings
        df = pd.DataFrame({
            'nazwa': ['Budynek A'],
            'adres': ['ul. Główna 1'],
            'kod_wydzialu': ['WI']
        })
        df.to_excel(writer, sheet_name='Budynki', index=False)
        
        # 3. rooms
        df = pd.DataFrame({
            'kod': ['A101'],
            'nazwa': ['Sala wykładowa'],
            'nazwa_budynku': ['Budynek A'],
            'pojemnosc': [60],
            'typ': ['lecture_hall'],
            'notatki': ['']
        })
        df.to_excel(writer, sheet_name='Sale', index=False)
        
        # 4. groups
        df = pd.DataFrame({
            'kod': ['1WI-INF'],
            'nazwa': ['Informatyka rok 1'],
            'kod_wydzialu': ['WI'],
            'liczba_studentow': [30],
            'parent_kod': ['']
        })
        df.to_excel(writer, sheet_name='Grupy', index=False)
        
        # 5. teachers
        df = pd.DataFrame({
            'imie': ['Jan'],
            'nazwisko': ['Kowalski'],
            'kod_wydzialu': ['WI']
        })
        df.to_excel(writer, sheet_name='Prowadzacy', index=False)
        
        # 6. courses
        df = pd.DataFrame({
            'kod': ['INF-PROG1'],
            'nazwa': ['Programowanie 1'],
            'kod_wydzialu': ['WI'],
            'typ': ['lecture'],
            'godziny_semestr': [30]
        })
        df.to_excel(writer, sheet_name='Przedmioty', index=False)
        
        # 7. assignments
        df = pd.DataFrame({
            'kod_przedmiotu': ['INF-PROG1'],
            'kod_grupy': ['1WI-INF'],
            'prowadzacy': ['Jan Kowalski'],
            'semestr': ['2024Z']
        })
        df.to_excel(writer, sheet_name='Przypisania', index=False)
    
    output.seek(0)
    return output