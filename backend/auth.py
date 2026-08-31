"""
Author: M-Pistillucci
Year: 2026

Authentication and Pairing Manager for Google Meet StreamController Plugin.
"""

import logging
from typing import Dict, List, Any, Optional

LOG = logging.getLogger(__name__)


class AuthManager:
    """
    Gestisce l'autenticazione, la lista di istanze autorizzate (Pairing)
    e la validazione delle connessioni WebSocket provenienti dall'estensione del browser.
    """

    def __init__(self, backend=None):
        self.backend = backend
        # Struttura per tracciare le chiavi approvate: {extension_id: [instance_ids]}
        self.authorized_instances: Dict[str, List[str]] = {}
        # Struttura per le richieste di pairing in attesa: {instance_id: details}
        self.pending_requests: Dict[str, Dict[str, Any]] = {}

    def is_authorized(self, extension_id: str, instance_id: str) -> bool:
        """Verifica se una determinata istanza dell'estensione è autorizzata."""
        if extension_id in self.authorized_instances:
            return instance_id in self.authorized_instances[extension_id]
        return False

    def add_pending_request(self, extension_id: str, instance_id: str, client_info: Optional[Dict[str, Any]] = None):
        """Registra una nuova richiesta di pairing in attesa di approvazione dall'utente."""
        request_key = f"{extension_id}:{instance_id}"
        self.pending_requests[request_key] = {
            "extension_id": extension_id,
            "instance_id": instance_id,
            "info": client_info or {}
        }
        LOG.info(f"Nuova richiesta di pairing registrata per {request_key}")

    def approve_instance(self, extension_id: str, instance_id: str):
        """Approva un'istanza e la aggiunge alla whitelist."""
        if extension_id not in self.authorized_instances:
            self.authorized_instances[extension_id] = []

        if instance_id not in self.authorized_instances[extension_id]:
            self.authorized_instances[extension_id].append(instance_id)

        # Rimuove la richiesta da quelle in sospeso
        request_key = f"{extension_id}:{instance_id}"
        self.pending_requests.pop(request_key, None)
        LOG.info(f"Istanza approvata con successo: {request_key}")

    def deny_instance(self, extension_id: str, instance_id: str):
        """Rifiuta e rimuove una richiesta di pairing."""
        request_key = f"{extension_id}:{instance_id}"
        self.pending_requests.pop(request_key, None)
        LOG.info(f"Istanza rifiutata: {request_key}")

    def revoke_instance(self, extension_id: str, instance_id: str):
        """Revoca un'autorizzazione concessa in precedenza."""
        if extension_id in self.authorized_instances:
            if instance_id in self.authorized_instances[extension_id]:
                self.authorized_instances[extension_id].remove(instance_id)
                LOG.info(f"Autorizzazione revocata per {extension_id}:{instance_id}")

    def get_authorized_instances(self) -> List[Dict[str, str]]:
        """Restituisce la lista di tutte le istanze autorizzate."""
        result = []
        for ext_id, instances in self.authorized_instances.items():
            for inst_id in instances:
                result.append({"extension_id": ext_id, "instance_id": inst_id})
        return result

    def get_pending_pairing_requests(self) -> List[Dict[str, Any]]:
        """Restituisce tutte le richieste di pairing in sospeso."""
        return list(self.pending_requests.values())
