class Config:
    SQLITE_DB_PATH = 'train_delays.db'
    ENTUR_CLIENT_ID = 'din-nye-client-id-fra-entur'
    ENTUR_API_URL = 'https://api.entur.io/realtime/v1/rest/et'
    ENTUR_DATASET_ID = 'NSB'
    # Øker til 20 sekunder mellom hver forespørsel (3 per minutt for å være sikker)
    UPDATE_INTERVAL = 20
    # Minimum tid mellom API-kall (i sekunder)
    API_RATE_LIMIT = 20 