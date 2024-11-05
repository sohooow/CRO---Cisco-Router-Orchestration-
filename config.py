import xml.etree.ElementTree as ET

class Configuration():
    # Méthode permettant de récupérer les valeurs des clés du fichier app.config
    def __getitem__(self, key):
        settings = ET.parse('web.config').getroot().find('appSettings')
        return settings.find(f"add[@key='{key}']").get('value')