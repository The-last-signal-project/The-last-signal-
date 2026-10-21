#[macro_export]
macro_rules! tls_info {
    ($($arg:tt)*) => {
        log::info!(
            "[{}:{}] {}",
            file!(),
            line!(),
            format!($($arg)*)
        );
    };
}

#[macro_export]
macro_rules! tls_warn {
    ($($arg:tt)*) => {
        log::warn!(
            "[{}:{}] {}",
            file!(),
            line!(),
            format!($($arg)*)
        );
    };
}

#[macro_export]
macro_rules! tls_error {
    ($($arg:tt)*) => {
        log::error!(
            "[{}:{}] {}",
            file!(),
            line!(),
            format!($($arg)*)
        );
    };
}

#[macro_export]
macro_rules! tls_debug {
    ($($arg:tt)*) => {
        log::debug!(
            "[{}:{}] {}",
            file!(),
            line!(),
            format!($($arg)*)
        );
    };
}
