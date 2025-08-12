import os
import sys
import asyncio
import requests
from typing import Optional
from dotenv import load_dotenv
import logging
import json
from datetime import datetime, date, time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsoleInterface:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.session_token = None
        self.current_user = None

    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Print application header"""
        print("=" * 50)
        print("    GERESACO - Gestor de Reservas de Salas")
        print("=" * 50)
        print()

    def print_menu(self):
        """Print main menu options"""
        print("Seleccione una opción:")
        
        if not self.session_token:
            print("1. Registrarse")
            print("2. Iniciar sesión")
        else:
            print("1. Ver mi perfil")
            print("2. Ver mis reservas")
            print("3. Listar salas")
            print("4. Hacer una reserva")
            print("5. Cerrar sesión")
        
        print("9. Salir")
        print()

    def get_user_input(self, prompt: str, password: bool = False) -> str:
        """Get user input with optional password masking"""
        if password:
            import getpass
            return getpass.getpass(prompt)
        else:
            return input(prompt).strip()

    def validate_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_date(self, date_str: str) -> bool:
        """Validate date format YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def validate_time(self, time_str: str) -> bool:
        """Validate time format HH:MM"""
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False

    def make_authenticated_request(self, method: str, endpoint: str, data: dict = None) -> requests.Response:
        """Make an authenticated request with proper headers"""
        if not self.session_token:
            raise Exception("No authentication token available")
        
        # Clean the token (remove any whitespace)
        clean_token = self.session_token.strip()
        
        headers = {
            "Authorization": f"Bearer {clean_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
            
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    def register_user(self):
        """Handle user registration"""
        print("\n--- REGISTRO DE USUARIO ---")
        print()

        # Get user information
        while True:
            nombre = self.get_user_input("Ingrese su nombre completo: ")
            if nombre:
                break
            print("❌ El nombre no puede estar vacío.")

        while True:
            email = self.get_user_input("Ingrese su email: ")
            if email and self.validate_email(email):
                break
            print("❌ Por favor ingrese un email válido.")

        while True:
            password = self.get_user_input("Ingrese su contraseña (mínimo 6 caracteres): ", password=True)
            if len(password) >= 6:
                break
            print("❌ La contraseña debe tener al menos 6 caracteres.")

        # Optional role selection (default to user)
        print("\nSeleccione su rol:")
        print("1. Usuario (por defecto)")
        print("2. Administrador")
        rol_choice = self.get_user_input("Opción (1-2, Enter para usuario): ")
        rol = "admin" if rol_choice == "2" else "user"

        # Make API request
        try:
            payload = {
                "nombre": nombre,
                "email": email,
                "contrasena": password,
                "rol": rol
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/register",
                json=payload,
                headers=headers
            )

            if response.status_code == 201:
                data = response.json()
                
                # Store the token properly
                self.session_token = data["access_token"].strip()
                self.current_user = {
                    "id": data["user_id"],
                    "role": data["user_role"],
                    "email": email,
                    "nombre": nombre
                }
                
                print(f"\n✅ ¡Registro exitoso! Bienvenido/a, {nombre}")
                print(f"🔑 Sesión iniciada correctamente")
                
                return True
            else:
                try:
                    error_data = response.json()
                    print(f"\n❌ Error en el registro: {error_data.get('detail', 'Error desconocido')}")
                except:
                    print(f"\n❌ Error en el registro: {response.text}")
                return False

        except requests.exceptions.ConnectionError:
            print("\n❌ Error: No se pudo conectar al servidor. Asegúrese de que la API esté ejecutándose.")
            return False
        except Exception as e:
            print(f"\n❌ Error inesperado: {str(e)}")
            return False

    def login_user(self):
        """Handle user login"""
        print("\n--- INICIAR SESIÓN ---")
        print()

        # Get login credentials
        while True:
            email = self.get_user_input("Email: ")
            if email and self.validate_email(email):
                break
            print("❌ Por favor ingrese un email válido.")

        password = self.get_user_input("Contraseña: ", password=True)

        # Make API request
        try:
            payload = {
                "email": email,
                "contrasena": password
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                
                # Store the token properly
                self.session_token = data["access_token"].strip()
                self.current_user = {
                    "id": data["user_id"],
                    "role": data["user_role"],
                    "email": email
                }
                
                print(f"\n✅ ¡Inicio de sesión exitoso!")
                print(f"🔑 Sesión iniciada correctamente")
                
                return True
            else:
                try:
                    error_data = response.json()
                    print(f"\n❌ Error en el inicio de sesión: {error_data.get('detail', 'Credenciales incorrectas')}")
                except:
                    print(f"\n❌ Error en el inicio de sesión: {response.text}")
                return False

        except requests.exceptions.ConnectionError:
            print("\n❌ Error: No se pudo conectar al servidor. Asegúrese de que la API esté ejecutándose.")
            return False
        except Exception as e:
            print(f"\n❌ Error inesperado: {str(e)}")
            return False

    def logout_user(self):
        """Handle user logout"""
        self.session_token = None
        self.current_user = None
        print("\n✅ Sesión cerrada correctamente.")

    def show_user_info(self):
        """Show current user information"""
        if not self.session_token:
            print("\n❌ No hay sesión activa.")
            return

        try:
            response = self.make_authenticated_request("GET", "/auth/me")
            if response.status_code == 200:
                user_data = response.json()
                print(f"\n👤 Usuario actual: {user_data['nombre']} ({user_data['email']})")
                print(f"🏷️  Rol: {user_data['rol']}")
            else:
                print("\n❌ No se pudo obtener la información del usuario.")
                print(f"Error: {response.text}")

        except Exception as e:
            print(f"\n❌ Error al obtener información del usuario: {str(e)}")

    def show_user_profile(self):
        """Show detailed user profile"""
        if not self.session_token:
            print("❌ No hay sesión activa.")
            return

        print("\n--- MI PERFIL ---")
        try:
            response = self.make_authenticated_request("GET", "/users/me")
            if response.status_code == 200:
                user_data = response.json()
                print(f"\n👤 Nombre: {user_data['nombre']}")
                print(f"📧 Email: {user_data['email']}")
                print(f"🏷️  Rol: {user_data['rol']}")
                print(f"🆔 ID: {user_data['id']}")
            else:
                print(f"❌ Error obteniendo perfil: {response.text}")
        except Exception as e:
            print(f"❌ Error obteniendo perfil: {str(e)}")

    def show_user_reservations(self):
        """Show user reservations"""
        if not self.session_token:
            print("❌ No hay sesión activa.")
            return

        print("\n--- MIS RESERVAS ---")
        try:
            response = self.make_authenticated_request("GET", "/reservations/me")
            if response.status_code == 200:
                reservations = response.json()
                
                # Count reservations by status
                status_counts = {}
                for res in reservations:
                    status = res['estado']
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Display status summary
                status_summary = []
                if status_counts.get('confirmada', 0) > 0:
                    status_summary.append(f"✅ {status_counts['confirmada']} confirmadas")
                if status_counts.get('pendiente', 0) > 0:
                    status_summary.append(f"⏳ {status_counts['pendiente']} pendientes")
                if status_counts.get('cancelada', 0) > 0:
                    status_summary.append(f"❌ {status_counts['cancelada']} canceladas")
                
                print(f"\n📅 Total de reservas: {len(reservations)}")
                if status_summary:
                    print(f"📊 Resumen: {' | '.join(status_summary)}")
                
                if reservations:
                    print("\nDetalle de reservas:")
                    for i, res in enumerate(reservations, 1):
                        sala_info = res.get('sala', {})
                        sala_nombre = sala_info.get('nombre', 'N/A') if sala_info else 'N/A'
                        
                        # Status emoji mapping
                        status_emoji = {
                            "pendiente": "⏳",
                            "confirmada": "✅", 
                            "cancelada": "❌"
                        }
                        status_display = f"{status_emoji.get(res['estado'], '📊')} {res['estado'].upper()}"

                        print(f"\n{i}. Reserva ID: {res['id']}")
                        print(f"   📅 Fecha: {res['fecha']}")
                        print(f"   ⏰ Horario: {res['hora_inicio']} - {res['hora_fin']}")
                        print(f"   🏢 Sala: {sala_nombre}")
                        print(f"   📊 Estado: {status_display}")
                else:
                    print("\nNo tienes reservas registradas.")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    def list_rooms(self):
        """List available rooms"""
        if not self.session_token:
            print("❌ No hay sesión activa.")
            return

        print("\n--- SALAS DISPONIBLES ---")
        try:
            response = self.make_authenticated_request("GET", "/rooms/")
            if response.status_code == 200:
                rooms = response.json()
                print(f"\n🏢 Total de salas: {len(rooms)}")
                
                if rooms:
                    print("\nDetalle de salas:")
                    for i, room in enumerate(rooms, 1):
                        print(f"\n{i}. {room['nombre']}")
                        print(f"   🏢 Sede: {room['sede']}")
                        print(f"   👥 Capacidad: {room['capacidad']} personas")
                        print(f"   🛠️  Recursos: {room['recursos']}")
                        print(f"   🆔 ID: {room['id']}")
                else:
                    print("\nNo hay salas disponibles.")
                
                return rooms
            else:
                print(f"❌ Error: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []

    def make_reservation(self):
        """Create a new reservation"""
        if not self.session_token:
            print("❌ No hay sesión activa.")
            return

        print("\n--- HACER UNA RESERVA ---")
        print()

        # First, get and show available rooms
        print("📋 Consultando salas disponibles...")
        try:
            response = self.make_authenticated_request("GET", "/rooms/")
            if response.status_code != 200:
                print(f"❌ Error obteniendo salas: {response.text}")
                return
            
            rooms = response.json()
            if not rooms:
                print("❌ No hay salas disponibles.")
                return

            print(f"\n🏢 Salas disponibles ({len(rooms)}):")
            for i, room in enumerate(rooms, 1):
                print(f"{i}. {room['nombre']} (ID: {room['id']}) - {room['sede']} - Cap: {room['capacidad']}")

        except Exception as e:
            print(f"❌ Error obteniendo salas: {str(e)}")
            return

        # Get room selection
        while True:
            try:
                room_choice = self.get_user_input("\nSeleccione el número de sala (o 'c' para cancelar): ")
                if room_choice.lower() == 'c':
                    print("❌ Reserva cancelada.")
                    return
                
                room_index = int(room_choice) - 1
                if 0 <= room_index < len(rooms):
                    selected_room = rooms[room_index]
                    break
                else:
                    print(f"❌ Opción inválida. Seleccione un número entre 1 y {len(rooms)}.")
            except ValueError:
                print("❌ Por favor ingrese un número válido.")

        print(f"\n✅ Sala seleccionada: {selected_room['nombre']}")

        # Get reservation date
        while True:
            fecha_str = self.get_user_input("Ingrese la fecha de reserva (YYYY-MM-DD): ")
            if self.validate_date(fecha_str):
                # Check if date is not in the past
                reservation_date = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                if reservation_date >= date.today():
                    break
                else:
                    print("❌ La fecha no puede ser anterior a hoy.")
            else:
                print("❌ Formato de fecha inválido. Use YYYY-MM-DD (ej: 2024-12-25)")

        # Get start time
        while True:
            hora_inicio_str = self.get_user_input("Ingrese la hora de inicio (HH:MM, formato 24h): ")
            if self.validate_time(hora_inicio_str):
                break
            else:
                print("❌ Formato de hora inválido. Use HH:MM (ej: 14:30)")

        # Calculate end time (1 hour later as per business rules)
        try:
            start_time = datetime.strptime(hora_inicio_str, '%H:%M').time()
            start_datetime = datetime.combine(date.today(), start_time)
            end_datetime = start_datetime.replace(hour=start_datetime.hour + 1)
            hora_fin_str = end_datetime.strftime('%H:%M')
            
            print(f"⏰ Duración de la reserva: 1 hora ({hora_inicio_str} - {hora_fin_str})")
            
        except Exception as e:
            print(f"❌ Error calculando hora de fin: {str(e)}")
            return

        # Create reservation with "pendiente" status first
        print(f"\n📋 RESUMEN DE LA RESERVA:")
        print(f"🏢 Sala: {selected_room['nombre']}")
        print(f"📍 Sede: {selected_room['sede']}")
        print(f"📅 Fecha: {fecha_str}")
        print(f"⏰ Horario: {hora_inicio_str} - {hora_fin_str}")
        print(f"📊 Estado inicial: pendiente")

        # Create reservation with "pendiente" status
        try:
            reservation_data = {
                "usuario_id": self.current_user["id"],
                "sala_id": selected_room["id"],
                "fecha": fecha_str,
                "hora_inicio": hora_inicio_str,
                "hora_fin": hora_fin_str,
                "estado": "pendiente"
            }

            response = self.make_authenticated_request("POST", "/reservations/", reservation_data)
            
            if response.status_code == 201:
                reservation = response.json()
                print(f"\n⏳ Reserva creada con estado 'pendiente'")
                print(f"🆔 ID de reserva: {reservation['id']}")
                
                # Ask for confirmation
                confirm = self.get_user_input("\n¿Confirmar reserva? (s/n): ").lower()
                if confirm == 's':
                    # Update reservation status to "confirmada"
                    update_data = {"estado": "confirmada"}
                    update_response = self.make_authenticated_request(
                        "PATCH", 
                        f"/reservations/{reservation['id']}", 
                        update_data
                    )
                    
                    if update_response.status_code == 200:
                        updated_reservation = update_response.json()
                        print(f"\n✅ ¡Reserva confirmada exitosamente!")
                        print(f"🆔 ID de reserva: {updated_reservation['id']}")
                        print(f"📅 Fecha: {updated_reservation['fecha']}")
                        print(f"⏰ Horario: {updated_reservation['hora_inicio']} - {updated_reservation['hora_fin']}")
                        print(f"📊 Estado: {updated_reservation['estado']}")
                    else:
                        print(f"\n❌ Error confirmando reserva: {update_response.text}")
                        print("La reserva permanece en estado 'pendiente'")
                else:
                    print(f"\n⏳ Reserva mantenida en estado 'pendiente'")
                    print("Puede confirmarla más tarde desde 'Ver mis reservas'")
                    
            else:
                try:
                    error_data = response.json()
                    print(f"\n❌ Error creando reserva: {error_data.get('detail', 'Error desconocido')}")
                except:
                    print(f"\n❌ Error creando reserva: {response.text}")

        except Exception as e:
            print(f"\n❌ Error inesperado creando reserva: {str(e)}")

    def wait_for_enter(self):
        """Wait for user to press Enter"""
        input("\nPresione Enter para continuar...")

    def run(self):
        """Main console interface loop"""
        while True:
            self.clear_screen()
            self.print_header()
            
            # Show current user if logged in
            if self.session_token:
                self.show_user_info()
                print()

            self.print_menu()

            try:
                choice = self.get_user_input("Ingrese su opción: ")

                # Handle options based on session state
                if not self.session_token:
                    # Not logged in - show register/login options
                    if choice == "1":
                        success = self.register_user()
                        if success:
                            print(f"\n🎉 ¡Bienvenido al sistema!")
                        self.wait_for_enter()

                    elif choice == "2":
                        success = self.login_user()
                        if success:
                            print(f"\n🎉 ¡Bienvenido de vuelta!")
                        self.wait_for_enter()

                    elif choice == "9":
                        print("\n👋 ¡Hasta luego!")
                        break

                    else:
                        print("\n❌ Opción inválida. Debe iniciar sesión primero.")
                        self.wait_for_enter()

                else:
                    # Logged in - show authenticated options
                    if choice == "1":
                        self.show_user_profile()
                        self.wait_for_enter()

                    elif choice == "2":
                        self.show_user_reservations()
                        self.wait_for_enter()

                    elif choice == "3":
                        self.list_rooms()
                        self.wait_for_enter()

                    elif choice == "4":
                        self.make_reservation()
                        self.wait_for_enter()

                    elif choice == "5":
                        self.logout_user()
                        self.wait_for_enter()

                    elif choice == "9":
                        print("\n👋 ¡Hasta luego!")
                        break

                    else:
                        print("\n❌ Opción inválida.")
                        self.wait_for_enter()

            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error inesperado: {str(e)}")
                self.wait_for_enter()

def start_console_interface():
    """Start the console interface"""
    interface = ConsoleInterface()
    interface.run()

if __name__ == "__main__":
    start_console_interface()
