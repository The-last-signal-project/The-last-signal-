pub fn parse_login_payload(
    payload: &[u8],
) -> Result<(String, String), String> {

    let mut offset = 0;

    // -------------------------
    // Email length
    // -------------------------

    if payload.len() < offset + 2 {
        return Err("Email length manquante".into());
    }

    let email_length =
        u16::from_be_bytes([
            payload[offset],
            payload[offset + 1],
        ]) as usize;

    offset += 2;

    // -------------------------
    // Email
    // -------------------------

    if payload.len() < offset + email_length {
        return Err("Email incomplet".into());
    }

    let email = String::from_utf8(
        payload[offset..offset + email_length]
            .to_vec()
    )
    .map_err(|_| "Email UTF-8 invalide")?;

    offset += email_length;

    // -------------------------
    // Password length
    // -------------------------

    if payload.len() < offset + 2 {
        return Err("Password length manquante".into());
    }

    let password_length =
        u16::from_be_bytes([
            payload[offset],
            payload[offset + 1],
        ]) as usize;

    offset += 2;

    // -------------------------
    // Password
    // -------------------------

    if payload.len() < offset + password_length {
        return Err("Password incomplet".into());
    }

    let password = String::from_utf8(
        payload[offset..offset + password_length]
            .to_vec()
    )
    .map_err(|_| "Password UTF-8 invalide")?;

    Ok((email, password))
}
pub fn parse_signup_payload(
    payload: &[u8],
) -> Result<(String, String), String> {

    let mut offset = 0;

    // -------------------------
    // Email length
    // -------------------------

    if payload.len() < offset + 2 {
        return Err("Email length manquante".into());
    }

    let email_length =
        u16::from_be_bytes([
            payload[offset],
            payload[offset + 1],
        ]) as usize;

    offset += 2;

    // -------------------------
    // Email
    // -------------------------

    if payload.len() < offset + email_length {
        return Err("Email incomplet".into());
    }

    let email = String::from_utf8(
        payload[offset..offset + email_length]
            .to_vec()
    )
    .map_err(|_| "Email UTF-8 invalide")?;

    offset += email_length;

    // -------------------------
    // Password length
    // -------------------------

    if payload.len() < offset + 2 {
        return Err("Password length manquante".into());
    }

    let password_length =
        u16::from_be_bytes([
            payload[offset],
            payload[offset + 1],
        ]) as usize;

    offset += 2;

    // -------------------------
    // Password
    // -------------------------

    if payload.len() < offset + password_length {
        return Err("Password incomplet".into());
    }

    let password = String::from_utf8(
        payload[offset..offset + password_length]
            .to_vec()
    )
    .map_err(|_| "Password UTF-8 invalide")?;

    Ok((email, password))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn build_payload(email: &[u8], password: &[u8]) -> Vec<u8> {
        let mut bytes = Vec::new();
        bytes.extend_from_slice(&(email.len() as u16).to_be_bytes());
        bytes.extend_from_slice(email);
        bytes.extend_from_slice(&(password.len() as u16).to_be_bytes());
        bytes.extend_from_slice(password);
        bytes
    }

    #[test]
    fn test_login_payload_valid() {
        let payload = build_payload(b"player@signal.com", b"p@ssword123");
        let (email, password) = parse_login_payload(&payload).expect("valid login payload should succeed");
        assert_eq!(email, "player@signal.com");
        assert_eq!(password, "p@ssword123");
    }

    #[test]
    fn test_login_payload_empty() {
        let err = parse_login_payload(&[]).unwrap_err();
        assert_eq!(err, "Email length manquante");
    }

    #[test]
    fn test_login_payload_truncated_email_length() {
        let err = parse_login_payload(&[0x00]).unwrap_err();
        assert_eq!(err, "Email length manquante");
    }

    #[test]
    fn test_login_payload_truncated_email_body() {
        let mut payload = vec![0x00, 0x0A]; // claims 10 bytes
        payload.extend_from_slice(b"short"); // only 5 bytes
        let err = parse_login_payload(&payload).unwrap_err();
        assert_eq!(err, "Email incomplet");
    }

    #[test]
    fn test_login_payload_invalid_email_utf8() {
        let invalid_utf8 = vec![0xFF, 0xFE, 0xFD];
        let payload = build_payload(&invalid_utf8, b"secret");
        let err = parse_login_payload(&payload).unwrap_err();
        assert_eq!(err, "Email UTF-8 invalide");
    }

    #[test]
    fn test_login_payload_missing_password_length() {
        let mut payload = vec![0x00, 0x04];
        payload.extend_from_slice(b"user"); // ends immediately after email
        let err = parse_login_payload(&payload).unwrap_err();
        assert_eq!(err, "Password length manquante");
    }

    #[test]
    fn test_login_payload_truncated_password_length() {
        let mut payload = vec![0x00, 0x04];
        payload.extend_from_slice(b"user");
        payload.push(0x00); // 1 byte only for password length
        let err = parse_login_payload(&payload).unwrap_err();
        assert_eq!(err, "Password length manquante");
    }

    #[test]
    fn test_login_payload_truncated_password_body() {
        let mut payload = vec![0x00, 0x04];
        payload.extend_from_slice(b"user");
        payload.extend_from_slice(&[0x00, 0x10]); // claims 16 bytes
        payload.extend_from_slice(b"short"); // only 5 bytes
        let err = parse_login_payload(&payload).unwrap_err();
        assert_eq!(err, "Password incomplet");
    }

    #[test]
    fn test_login_payload_invalid_password_utf8() {
        let invalid_utf8 = vec![0xC3, 0x28]; // invalid 2-byte UTF-8 sequence
        let payload = build_payload(b"user@test.com", &invalid_utf8);
        let err = parse_login_payload(&payload).unwrap_err();
        assert_eq!(err, "Password UTF-8 invalide");
    }

    #[test]
    fn test_login_payload_trailing_bytes_accepted() {
        let mut payload = build_payload(b"user@test.com", b"mypassword");
        payload.extend_from_slice(&[0xAA, 0xBB, 0xCC, 0xDD]);
        let (email, password) = parse_login_payload(&payload).expect("trailing bytes should not panic or fail");
        assert_eq!(email, "user@test.com");
        assert_eq!(password, "mypassword");
    }

    #[test]
    fn test_signup_payload_valid() {
        let payload = build_payload(b"newuser@signal.com", b"securepass99");
        let (email, password) = parse_signup_payload(&payload).expect("valid signup payload should succeed");
        assert_eq!(email, "newuser@signal.com");
        assert_eq!(password, "securepass99");
    }

    #[test]
    fn test_signup_payload_empty() {
        let err = parse_signup_payload(&[]).unwrap_err();
        assert_eq!(err, "Email length manquante");
    }

    #[test]
    fn test_signup_payload_truncated_email_length() {
        let err = parse_signup_payload(&[0x01]).unwrap_err();
        assert_eq!(err, "Email length manquante");
    }

    #[test]
    fn test_signup_payload_truncated_email_body() {
        let mut payload = vec![0x00, 0x06];
        payload.extend_from_slice(b"abc");
        let err = parse_signup_payload(&payload).unwrap_err();
        assert_eq!(err, "Email incomplet");
    }

    #[test]
    fn test_signup_payload_invalid_email_utf8() {
        let invalid_utf8 = vec![0xED, 0xA0, 0x80]; // surrogate half in UTF-8
        let payload = build_payload(&invalid_utf8, b"validpass");
        let err = parse_signup_payload(&payload).unwrap_err();
        assert_eq!(err, "Email UTF-8 invalide");
    }

    #[test]
    fn test_signup_payload_missing_password_length() {
        let mut payload = vec![0x00, 0x05];
        payload.extend_from_slice(b"admin");
        let err = parse_signup_payload(&payload).unwrap_err();
        assert_eq!(err, "Password length manquante");
    }

    #[test]
    fn test_signup_payload_truncated_password_length() {
        let mut payload = vec![0x00, 0x05];
        payload.extend_from_slice(b"admin");
        payload.push(0x00);
        let err = parse_signup_payload(&payload).unwrap_err();
        assert_eq!(err, "Password length manquante");
    }

    #[test]
    fn test_signup_payload_truncated_password_body() {
        let mut payload = vec![0x00, 0x05];
        payload.extend_from_slice(b"admin");
        payload.extend_from_slice(&[0x00, 0x08]);
        payload.extend_from_slice(b"two");
        let err = parse_signup_payload(&payload).unwrap_err();
        assert_eq!(err, "Password incomplet");
    }

    #[test]
    fn test_signup_payload_invalid_password_utf8() {
        let invalid_utf8 = vec![0xF4, 0x90, 0x80, 0x80]; // codepoint beyond Unicode
        let payload = build_payload(b"admin@signal.com", &invalid_utf8);
        let err = parse_signup_payload(&payload).unwrap_err();
        assert_eq!(err, "Password UTF-8 invalide");
    }

    #[test]
    fn test_signup_payload_trailing_bytes_accepted() {
        let mut payload = build_payload(b"admin@signal.com", b"rootpass");
        payload.extend_from_slice(b"extraneous data");
        let (email, password) = parse_signup_payload(&payload).expect("trailing bytes should not panic or fail");
        assert_eq!(email, "admin@signal.com");
        assert_eq!(password, "rootpass");
    }
}
