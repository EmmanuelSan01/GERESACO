USE geresaco;

INSERT INTO user (nombre, contrasena_hash, rol, email) VALUES
('Juan Pérez', 'hash123456', 'admin', 'juan.perez@geresaco.com'),
('María Gómez', 'hash789012', 'user', 'maria.gomez@geresaco.com'),
('Carlos López', 'hash345678', 'user', 'carlos.lopez@geresaco.com'),
('Ana Martínez', 'hash901234', 'admin', 'ana.martinez@geresaco.com');

INSERT INTO room (nombre, sede, capacidad, recursos) VALUES
('Sala de Juntas 1', 'zona_franca', 10, 'Proyector, Pizarra, WiFi'),
('Sala de Capacitación', 'cajasan', 20, 'Proyector, Computadores, WiFi'),
('Sala Ejecutiva', 'bogota', 8, 'Proyector, TV, WiFi'),
('Sala de Reuniones', 'cucuta', 12, 'Pizarra, WiFi'),
('Sala Principal', 'guatemala', 15, 'Proyector, Pizarra, WiFi');

INSERT INTO reservation (fecha, hora_inicio, hora_fin, estado, usuario_id, sala_id) VALUES
('2025-08-15', '09:00:00', '11:00:00', 'confirmada', 1, 1),
('2025-08-15', '14:00:00', '16:00:00', 'pendiente', 2, 2),
('2025-08-16', '10:00:00', '12:00:00', 'confirmada', 3, 3),
('2025-08-16', '15:00:00', '17:00:00', 'cancelada', 4, 4),
('2025-08-17', '08:00:00', '10:00:00', 'pendiente', 1, 5);