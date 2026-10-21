use uuid::Uuid;

#[derive(Debug, Clone, Default)]
pub struct LogContext {
    pub session_id: Option<Uuid>,
    pub client_id: Option<i64>,
    pub account_id: Option<Uuid>,
}
