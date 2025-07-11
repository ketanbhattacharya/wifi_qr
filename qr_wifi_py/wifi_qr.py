import subprocess
import re
import qrcode

def get_current_connected_ssid():
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, encoding="utf-8", errors="ignore")
        match = re.search(r"^\s*SSID\s*:\s(.+)", output, re.MULTILINE)
        if match:
            return match.group(1).strip()
    except subprocess.CalledProcessError:
        pass
    return None

def get_saved_wifi_profiles():
    output = subprocess.check_output("netsh wlan show profiles", shell=True, encoding="utf-8", errors="ignore")
    profiles = re.findall(r"All User Profile\s*:\s*(.*)", output)
    return [profile.strip() for profile in profiles]

def get_wifi_password(profile_name):
    try:
        output = subprocess.check_output(
            f'netsh wlan show profile name="{profile_name}" key=clear',
            shell=True,
            encoding="utf-8",
            errors="ignore"
        )
        password_match = re.search(r"Key Content\s*:\s*(.*)", output)
        if password_match:
            return password_match.group(1)
        else:
            return None
    except subprocess.CalledProcessError:
        return None

def generate_wifi_qr_code(ssid, password, auth_type="WPA"):
    wifi_string = f'WIFI:S:"{ssid}";T:{auth_type};P:"{password}";;'
    qr = qrcode.QRCode(border=2)
    qr.add_data(wifi_string)
    qr.make(fit=True)
    qr.print_ascii(invert=True)

def main():
    while True:
        current_ssid = get_current_connected_ssid()
        profiles = get_saved_wifi_profiles()

        if not profiles:
            print("No saved Wi-Fi profiles found.")
            return

        print("\n📡 Available Wi-Fi Profiles:\n")
        for i, profile in enumerate(profiles, 1):
            marker = " (Connected)" if profile == current_ssid else ""
            print(f"{i}. {profile}{marker}")

        print("0. Exit")
        choice = input("\nEnter the number of the Wi-Fi profile to view its password and QR code (or 0 to exit): ")

        if choice == "0":
            print("Goodbye!")
            break

        try:
            choice = int(choice)
            selected_profile = profiles[choice - 1]
        except (ValueError, IndexError):
            print("❌ Invalid selection. Please try again.")
            continue

        password = get_wifi_password(selected_profile)
        if password:
            print(f"\n🔐 Wi-Fi SSID: {selected_profile}")
            print(f"🔑 Password: {password}")
            print("\n📶 QR Code for Wi-Fi (scan this on mobile):\n")
            generate_wifi_qr_code(selected_profile, password)
        else:
            print("⚠️ Could not retrieve the password or password is not set.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
