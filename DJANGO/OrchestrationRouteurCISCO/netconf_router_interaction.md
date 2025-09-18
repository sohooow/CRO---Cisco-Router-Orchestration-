# Interaction entre le Routeur et NETCONF

## 1. Architecture générale

```
[Application Python] ←→ [NETCONF Client] ←→ [SSH] ←→ [Routeur NETCONF Server] ←→ [IOS Configuration]
                    ↘
                     [Netmiko] ←→ [SSH] ←→ [Routeur CLI] ←→ [IOS Configuration]
```

**Dans votre projet, vous utilisez DEUX méthodes :**

### A. SSH traditionnel (Netmiko)
```python
from netmiko import ConnectHandler  # ← SSH classique pour CLI

def ssh_configure_netmiko(config_commands):
    connection = ConnectHandler(**device)  # SSH sur port 22
    connection.enable()
    output = connection.send_config_set(config_commands)
```

### B. SSH pour NETCONF (ncclient)
```python
from ncclient import manager  # ← SSH spécialisé pour NETCONF

def ssh_configure_netconf(xml_payload):
    with manager.connect(
        host=device["host"],
        port=830,  # ← SSH sur port 830 (NETCONF)
        ...
    ) as m:
```

**Différence importante :**
- **SSH classique (port 22)** : Envoie des commandes textuelles CLI
- **SSH NETCONF (port 830)** : Envoie des messages XML NETCONF

Les deux utilisent SSH comme transport, mais pour des protocoles différents !

## 1.1 Qu'est-ce que le Client NETCONF ?

Le **Client NETCONF** est une bibliothèque Python qui fait le lien entre votre application et le routeur. C'est un intermédiaire intelligent qui traduit vos appels Python en messages NETCONF.

### A. Bibliothèque utilisée : `ncclient`
```python
from ncclient import manager  # ← Ceci est le client NETCONF
```

### B. Rôle du Client NETCONF
1. **Traduction** : Convertit les appels Python en XML NETCONF
2. **Communication** : Gère la connexion SSH avec le routeur
3. **Sérialisation** : Transforme les données Python en XML et vice-versa
4. **Gestion des sessions** : Maintient la session NETCONF active

### C. Ce que fait le Client NETCONF concrètement

#### Dans votre code :
```python
with manager.connect(...) as m:          # Client NETCONF se connecte
    response = m.edit_config(target="candidate", config=xml)  # Client traduit en XML
```

#### Ce que le Client NETCONF envoie au routeur :
```xml
<rpc message-id="1" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <edit-config>
    <target>
      <candidate/>
    </target>
    <config>
      <!-- Votre configuration XML ici -->
    </config>
  </edit-config>
</rpc>
```

### D. Analogie simple
- **Votre application** = Vous qui voulez envoyer un email
- **Client NETCONF** = Votre logiciel de messagerie (Gmail, Outlook)
- **Routeur** = Le serveur de messagerie du destinataire

Le client NETCONF gère tous les détails techniques de la communication NETCONF, vous n'avez qu'à lui dire quoi faire !

## 2. Composants du routeur

### A. NETCONF Server (sur le routeur)
- **Port d'écoute** : 830 (par défaut)
- **Protocole de transport** : SSH (sécurisé)
- **Rôle** : Écoute les requêtes NETCONF et les traduit en commandes IOS

### B. Datastores (zones de stockage)
```
┌─────────────────────────────────────────────────────┐
│                    ROUTEUR CISCO                    │
├─────────────────────────────────────────────────────┤
│  📁 startup-config                                  │
│     └─ Configuration chargée au démarrage           │
├─────────────────────────────────────────────────────┤
│  📁 running-config (ACTIF)                         │
│     └─ Configuration actuellement active            │
├─────────────────────────────────────────────────────┤
│  📁 candidate-config (BROUILLON)                   │
│     └─ Configuration en préparation                 │
└─────────────────────────────────────────────────────┘
```

## 3. Processus d'interaction détaillé

### Étape 1 : Connexion NETCONF
```python
# Client Python établit une connexion SSH
with manager.connect(
    host="172.16.10.11",  # IP du routeur
    port=830,              # Port NETCONF
    username="admin",      # Utilisateur routeur
    password="c79e97SGVg7dc"
) as m:
```

**Ce qui se passe sur le routeur :**
- Le serveur NETCONF authentifie l'utilisateur
- Une session NETCONF est créée
- Le routeur envoie ses capacités (capabilities)

### Étape 2 : edit-config (Préparation)
```xml
<rpc message-id="1" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <edit-config>
    <target>
      <candidate/>
    </target>
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>2.7</name>
            <encapsulation>
              <dot1Q>
                <vlan-id>7</vlan-id>
              </dot1Q>
            </encapsulation>
            <ip>
              <address>
                <primary>
                  <address>192.168.27.2</address>
                  <mask>255.255.255.0</mask>
                </primary>
              </address>
            </ip>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
  </edit-config>
</rpc>
```

**Ce qui se passe sur le routeur :**
1. Le serveur NETCONF reçoit le XML
2. Il valide la syntaxe YANG
3. Il traduit le XML en configuration IOS :
   ```
   interface GigabitEthernet2.7
    encapsulation dot1Q 7
    ip address 192.168.27.2 255.255.255.0
   ```
4. Il stocke cette configuration dans le **candidate datastore**
5. ⚠️ **IMPORTANT** : Cette configuration n'est PAS encore active !

### Étape 3 : commit (Application)
```xml
<rpc message-id="2" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <commit/>
</rpc>
```

**Ce qui se passe sur le routeur :**
1. Le routeur copie la configuration du candidate vers running
2. Il applique immédiatement les changements
3. L'interface GigabitEthernet2.7 devient active
4. La configuration est maintenant opérationnelle

## 4. Vérification côté routeur

### Commandes IOS pour vérifier :
```bash
# Vérifier les interfaces
show ip interface brief

# Vérifier la configuration running
show running-config interface GigabitEthernet2.7

# Vérifier NETCONF
show netconf-yang datastores
```

## 5. Flux de données complet

```
1. Python → NETCONF Client → SSH → Routeur
   [XML edit-config] → [Candidate datastore]

2. Python → NETCONF Client → SSH → Routeur  
   [XML commit] → [Running datastore] → [Interface active]

3. Routeur → SSH → NETCONF Client → Python
   [Réponse XML] ← [Confirmation]
```

## 6. Traduction NETCONF ↔ IOS

### XML NETCONF →
```xml
<GigabitEthernet>
  <name>2.7</name>
  <encapsulation>
    <dot1Q>
      <vlan-id>7</vlan-id>
    </dot1Q>
  </encapsulation>
  <ip>
    <address>
      <primary>
        <address>192.168.27.2</address>
        <mask>255.255.255.0</mask>
      </primary>
    </address>
  </ip>
</GigabitEthernet>
```

### ← Configuration IOS
```
interface GigabitEthernet2.7
 encapsulation dot1Q 7
 ip address 192.168.27.2 255.255.255.0
 no shutdown
```

## 7. Avantages de NETCONF

### A. Structuration et Validation
- **XML structuré** : Données organisées et hiérarchisées
- **Validation YANG** : Vérification automatique de la syntaxe et des contraintes
- **Schéma strict** : Prévention des erreurs de configuration

### B. Gestion Transactionnelle
- **Candidate datastore** : Configuration en mode brouillon
- **Commit atomique** : Tous les changements appliqués d'un coup
- **Rollback** : Possibilité d'annuler les modifications
- **Validation avant application** : Test de la configuration avant activation

### C. Programmabilité
- **API standardisée** : Interface cohérente entre fabricants
- **Parsing facile** : XML facilement traitable par les applications
- **Intégration DevOps** : Compatible avec les outils d'automatisation
- **Gestion d'erreurs** : Messages d'erreur structurés et détaillés

### D. Sécurité et Fiabilité
- **Authentification SSH** : Connexion sécurisée par défaut
- **Sessions persistantes** : Gestion des connexions optimisée
- **Verrouillage de configuration** : Évite les conflits entre utilisateurs
- **Audit trail** : Traçabilité des modifications

### E. Maintenance et Évolutivité
- **Indépendance du CLI** : Pas de dépendance aux changements de syntaxe
- **Versionning** : Gestion des versions de schémas
- **Interopérabilité** : Standard IETF multi-fabricants
- **Scalabilité** : Gestion efficace de configurations complexes

## 8. Gestion des erreurs

Si une erreur survient :
```xml
<rpc-error>
  <error-type>protocol</error-type>
  <error-tag>invalid-value</error-tag>
  <error-message>Invalid IP address format</error-message>
</rpc-error>
```

Le routeur peut :
- Rejeter la configuration
- Garder le candidate intact
- Permettre une correction avant commit
