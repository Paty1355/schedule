DO $$
BEGIN
    CREATE TYPE room_type AS ENUM (
        'lecture_hall',
        'classroom',
        'auditorium',
        'computer_lab',
        'chemistry_lab',
        'physics_lab',
        'biology_lab',
        'language_lab',
        'seminar_room',
        'workshop',
        'gym',
        'other'
);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE course_type AS ENUM (
        'lecture',
        'exercise',
        'seminar',
        'project',
        'computer_lab',
        'chemistry_lab',
        'physics_lab',
        'biology_lab',
        'language_lab',
        'workshop',
        'gym_class',
        'other'
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
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

-- 2. buildings
CREATE TABLE IF NOT EXISTS buildings (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    address TEXT,
    department_id INT REFERENCES departments(id) ON DELETE SET NULL
);
-- 3. rooms
CREATE TABLE IF NOT EXISTS rooms (
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
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    department_id INT REFERENCES departments(id) ON DELETE CASCADE,
    students_count INT CHECK (students_count > 0),
    accessibility_requirements JSONB,
    parent_group_id INT REFERENCES groups(id)
);

-- 5. teachers
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    department_id INT REFERENCES departments(id) ON DELETE CASCADE,
    accessibility JSONB
);

-- 6. courses
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    department_id INT REFERENCES departments(id) ON DELETE CASCADE,
    type course_type NOT NULL,
    hours_per_semester INT CHECK (hours_per_semester > 0)
    
);

-- 7. course_assignments
CREATE TABLE IF NOT EXISTS course_assignments (
    id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(id) ON DELETE CASCADE,
    group_id INT REFERENCES groups(id) ON DELETE CASCADE,
    teacher_id INT REFERENCES teachers(id) ON DELETE CASCADE,
    semester TEXT NOT NULL,
    note TEXT,
    UNIQUE (course_id, group_id, teacher_id, semester)
);

-- 8. assignments
CREATE TABLE IF NOT EXISTS assignments (
    id SERIAL PRIMARY KEY,
    course_assignment_id INT REFERENCES course_assignments(id) ON DELETE CASCADE,
    room_id INT REFERENCES rooms(id) ON DELETE CASCADE,
    weekday weekday_enum NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    duration_minutes INT GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (end_time - start_time)) / 60
    ) STORED,
    week_parity week_parity_enum DEFAULT 'both',
    note TEXT,
    CHECK (end_time > start_time)
);

-- 9. teacher_unavailabilities
CREATE TABLE IF NOT EXISTS teacher_unavailabilities (
    id SERIAL PRIMARY KEY,
    teacher_id INT REFERENCES teachers(id) ON DELETE CASCADE,
    weekday weekday_enum NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    reason TEXT,
    CHECK (start_time < end_time)
);

-- 10. group_unavailabilities
CREATE TABLE IF NOT EXISTS group_unavailabilities (
    id SERIAL PRIMARY KEY,
    group_id INT REFERENCES groups(id) ON DELETE CASCADE,
    weekday weekday_enum NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    reason TEXT,
    CHECK (start_time < end_time)
);