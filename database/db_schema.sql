DO $$
BEGIN
    CREATE TYPE room_type AS ENUM (
        'lecture_hall',
        'lab',
        'seminar_room',
        'classroom',
        'auditorium',
        'computer_lab',
        'other',
        'gym'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE course_type AS ENUM (
        'lecture',
        'lab',
        'seminar',
        'project',
        'exercise'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE week_parity_enum AS ENUM (
        'odd',
        'even',
        'both'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE accessibility_feature AS ENUM (
        'wheelchair_access',
        'lift',
        'hearing_aid',
        'braille',
        'low_vision_support'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE weekday_enum AS ENUM (
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;



-- 1. departments
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

-- 2. buildings
CREATE TABLE buildings (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    department_id INT REFERENCES departments(id) ON DELETE SET NULL
);

-- 3. rooms
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    building_id INT REFERENCES buildings(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    name TEXT,
    capacity INT CHECK (capacity > 0),
    type room_type NOT NULL,
    note TEXT,
    equipment JSONB,
    accessibility JSONB
);

-- 4. groups
CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    department_id INT REFERENCES departments(id) ON DELETE CASCADE,
    students_count INT CHECK (students_count > 0),
    accessibility_requirements JSONB,
    parent_group_id INT REFERENCES groups(id)
);

-- 5. teachers
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    department_id INT REFERENCES departments(id) ON DELETE CASCADE,
    accessibility JSONB
);

-- 6. courses
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    department_id INT REFERENCES departments(id) ON DELETE CASCADE,
    type course_type NOT NULL,
    hours_per_semester INT CHECK (hours_per_semester > 0)
    
);

-- 7. course_assignments
CREATE TABLE course_assignments (
    id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(id) ON DELETE CASCADE,
    group_id INT REFERENCES groups(id) ON DELETE CASCADE,
    teacher_id INT REFERENCES teachers(id) ON DELETE CASCADE,
    semester TEXT NOT NULL,
    note TEXT,
    UNIQUE (course_id, group_id, teacher_id, semester)
);

-- 8. time_slots
CREATE TABLE time_slots (
    id SERIAL PRIMARY KEY,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_order INT NOT NULL,
    duration_minutes INT GENERATED ALWAYS AS (EXTRACT(EPOCH FROM (end_time - start_time)) / 60) STORED,
    CHECK (end_time > start_time)
);

-- 9. assignments
CREATE TABLE assignments (
    id SERIAL PRIMARY KEY,
    course_assignment_id INT REFERENCES course_assignments(id) ON DELETE CASCADE,
    room_id INT REFERENCES rooms(id) ON DELETE CASCADE,
    weekday weekday_enum NOT NULL,
    time_slot_id INT REFERENCES time_slots(id) ON DELETE CASCADE,
    week_parity week_parity_enum DEFAULT 'both',
    note TEXT
);

-- 10. teacher_unavailabilities
CREATE TABLE teacher_unavailabilities (
    id SERIAL PRIMARY KEY,
    teacher_id INT REFERENCES teachers(id) ON DELETE CASCADE,
    weekday weekday_enum NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    reason TEXT,
    CHECK (start_time < end_time)
);

-- 11. group_unavailabilities
CREATE TABLE group_unavailabilities (
    id SERIAL PRIMARY KEY,
    group_id INT REFERENCES groups(id) ON DELETE CASCADE,
    weekday weekday_enum NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    reason TEXT,
    CHECK (start_time < end_time)
);
