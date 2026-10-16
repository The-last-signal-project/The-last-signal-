fn parse_length_prefixed_str(
    payload: &[u8],
    offset: &mut usize,
    field_name: &str,
) -> Result<String, String> {
    if payload.len() < *offset + 2 {
        return Err(format!("{field_name} length manquante"));
    }

    let field_len = u16::from_be_bytes([payload[*offset], payload[*offset + 1]]) as usize;

    *offset += 2;

    let end = match offset.checked_add(field_len) {
        Some(end) if end <= payload.len() => end,
        _ => return Err(format!("{field_name} incomplet")),
    };

    let field_str = std::str::from_utf8(&payload[*offset..end])
        .map_err(|_| format!("{field_name} UTF-8 invalide"))?;

    *offset = end;

    Ok(field_str.to_string())
}

fn parse_credentials_payload(payload: &[u8]) -> Result<(String, String), String> {
    let mut offset = 0;
    let email = parse_length_prefixed_str(payload, &mut offset, "Email")?;
    let password = parse_length_prefixed_str(payload, &mut offset, "Password")?;
    Ok((email, password))
}

pub fn parse_login_payload(payload: &[u8]) -> Result<(String, String), String> {
    parse_credentials_payload(payload)
}

pub fn parse_signup_payload(payload: &[u8]) -> Result<(String, String), String> {
    parse_credentials_payload(payload)
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
        let (email, password) =
            parse_login_payload(&payload).expect("valid login payload should succeed");
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
        let (email, password) =
            parse_login_payload(&payload).expect("trailing bytes should not panic or fail");
        assert_eq!(email, "user@test.com");
        assert_eq!(password, "mypassword");
    }

    #[test]
    fn test_signup_payload_valid() {
        let payload = build_payload(b"newuser@signal.com", b"securepass99");
        let (email, password) =
            parse_signup_payload(&payload).expect("valid signup payload should succeed");
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
        let (email, password) =
            parse_signup_payload(&payload).expect("trailing bytes should not panic or fail");
        assert_eq!(email, "admin@signal.com");
        assert_eq!(password, "rootpass");
    }

    #[test]
    fn test_login_payload_empty_strings() {
        let payload = build_payload(b"", b"");
        let (email, password) =
            parse_login_payload(&payload).expect("empty strings should be valid");
        assert_eq!(email, "");
        assert_eq!(password, "");
    }

    #[test]
    fn test_login_payload_large_u16_length_incomplet() {
        // u16::MAX length declared but payload is small
        let mut payload = vec![0xFF, 0xFF];
        payload.extend_from_slice(b"hello");
        let err = parse_login_payload(&payload).unwrap_err();
        assert_eq!(err, "Email incomplet");
    }

    #[test]
    fn test_signup_payload_empty_strings() {
        let payload = build_payload(b"", b"");
        let (email, password) =
            parse_signup_payload(&payload).expect("empty strings should be valid");
        assert_eq!(email, "");
        assert_eq!(password, "");
    }

    #[test]
    fn test_signup_payload_large_u16_length_incomplet() {
        let mut payload = vec![0xFF, 0xFF];
        payload.extend_from_slice(b"hello");
        let err = parse_signup_payload(&payload).unwrap_err();
        assert_eq!(err, "Email incomplet");
    }

    #[test]
    fn test_parse_credentials_multibyte_utf8_success() {
        let email = "joueur_éàç@signal.fr";
        let password = "clé_secrète_🔑";
        let payload = build_payload(email.as_bytes(), password.as_bytes());

        let (login_email, login_pass) =
            parse_login_payload(&payload).expect("login multibyte UTF-8 should parse cleanly");
        assert_eq!(login_email, email);
        assert_eq!(login_pass, password);

        let (signup_email, signup_pass) =
            parse_signup_payload(&payload).expect("signup multibyte UTF-8 should parse cleanly");
        assert_eq!(signup_email, email);
        assert_eq!(signup_pass, password);
    }

    #[test]
    fn test_parse_credentials_mid_codepoint_slice_rejected() {
        // "éé" is 4 bytes [0xC3, 0xA9, 0xC3, 0xA9].
        // Slicing 3 bytes takes [0xC3, 0xA9, 0xC3], splitting the second character mid-codepoint.
        let mut payload = Vec::new();
        payload.extend_from_slice(&(3u16).to_be_bytes()); // claims 3 bytes
        payload.extend_from_slice("éé".as_bytes()); // 4 bytes
        payload.extend_from_slice(&(4u16).to_be_bytes());
        payload.extend_from_slice(b"pass");

        let err = parse_login_payload(&payload).expect_err("mid-codepoint slice must fail");
        assert!(
            err.contains("UTF-8"),
            "Error should indicate invalid UTF-8 when sliced mid-codepoint: {err}"
        );
    }

    #[test]
    fn test_parse_credentials_char_count_prefix_misaligns_next_field() {
        // Client mistakenly sends chars().count() (2) instead of byte length (4) for "éé".
        // The parser reads "é", then misinterprets the remaining 2 bytes of "éé" [0xC3, 0xA9]
        // as the password length prefix (50089), failing with a Password length/incomplete error.
        let mut payload = Vec::new();
        payload.extend_from_slice(&(2u16).to_be_bytes());
        payload.extend_from_slice("éé".as_bytes());
        payload.extend_from_slice(&(4u16).to_be_bytes());
        payload.extend_from_slice(b"pass");

        let err = parse_login_payload(&payload).expect_err("misaligned field must fail");
        assert!(err.contains("Password"), "unexpected error: {err}");
    }

    #[test]
    fn test_parse_credentials_preserves_whitespace() {
        let email = "  user@signal.com  ";
        let password = "  pass with spaces  ";
        let payload = build_payload(email.as_bytes(), password.as_bytes());

        let (parsed_email, parsed_pass) =
            parse_login_payload(&payload).expect("whitespace should parse successfully");
        assert_eq!(
            parsed_email, email,
            "Leading/trailing whitespace in email must be preserved"
        );
        assert_eq!(
            parsed_pass, password,
            "Whitespace in password must be preserved"
        );
    }

    #[test]
    fn test_parse_credentials_long_strings() {
        let email = format!("user_{}@signal.com", "a".repeat(250));
        let password = "p".repeat(300);
        let payload = build_payload(email.as_bytes(), password.as_bytes());

        let (parsed_email, parsed_pass) =
            parse_login_payload(&payload).expect("300-byte strings should parse cleanly");
        assert_eq!(parsed_email, email);
        assert_eq!(parsed_pass, password);
    }

    #[test]
    fn test_parse_credentials_special_ascii_symbols() {
        let email = "special+user.tag@signal.io";
        let password = "!@#$%^&*()_+-=[]{}|;':\",.<>/?~";
        let payload = build_payload(email.as_bytes(), password.as_bytes());

        let (parsed_email, parsed_pass) =
            parse_login_payload(&payload).expect("symbols should parse cleanly");
        assert_eq!(parsed_email, email);
        assert_eq!(parsed_pass, password);
    }
}
