use flate2::{
    write::GzEncoder,
    Compression,
};
use log::info;


use std::{
    fs::{self, File},
    io::{self, BufReader},
    path::{Path, PathBuf},
};

pub struct LogCompressor;

impl LogCompressor {
    /// Compresse tous les fichiers .log sauf les `keep_latest`
    /// plus récents.
    pub fn compress_old_logs<P: AsRef<Path>>(
        log_directory: P,
        keep_latest: usize,
    ) -> io::Result<()> {

        let log_directory = log_directory.as_ref();

        if !log_directory.exists() {
            return Ok(());
        }

        let mut log_files = Self::collect_logs(log_directory)?;

        // Plus récent -> plus ancien
        log_files.sort_by(|a, b| {
            let time_a = Self::modified(a);
            let time_b = Self::modified(b);

            time_b.cmp(&time_a)
        });

        for file in log_files.into_iter().skip(keep_latest) {

            let compressed =
                file.with_extension("log.gz");

            // Déjà compressé
            if compressed.exists() {
                continue;
            }

            info!(
                "[LOGGER] Compression : {}",
                file.display()
            );

            Self::compress_file(&file, &compressed)?;

            fs::remove_file(file)?;
        }

        Ok(())
    }

    fn collect_logs(
        directory: &Path,
    ) -> io::Result<Vec<PathBuf>> {

        let mut files = Vec::new();

        for entry in fs::read_dir(directory)? {

            let entry = entry?;

            let path = entry.path();

            if !path.is_file() {
                continue;
            }

            let Some(name) =
                path.file_name().and_then(|n| n.to_str())
            else {
                continue;
            };

            // Ignore déjà compressés
            if name.ends_with(".log.gz") {
                continue;
            }

            if name.ends_with(".log") {
                files.push(path);
            }
        }

        Ok(files)
    }

    fn compress_file(
        input: &Path,
        output: &Path,
    ) -> io::Result<()> {

        let input_file = File::open(input)?;

        let output_file = File::create(output)?;

        let mut encoder =
            GzEncoder::new(
                output_file,
                Compression::default(),
            );

        let mut reader =
            BufReader::new(input_file);

        io::copy(
            &mut reader,
            &mut encoder,
        )?;

        encoder.finish()?;

        Ok(())
    }

    fn modified(
        path: &Path,
    ) -> std::time::SystemTime {

        fs::metadata(path)
            .and_then(|m| m.modified())
            .unwrap_or(std::time::UNIX_EPOCH)
    }
}
