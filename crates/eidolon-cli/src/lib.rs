use clap::Parser;

#[derive(Debug, Default, Parser)]
pub struct Cli {
    #[arg(short, long)]
    pub config: Option<String>,
    #[arg(short, long)]
    pub serve: bool,
    #[arg(short, long)]
    pub mesh: bool,
}

impl Cli {
    pub fn new() -> Self {
        Self::parse()
    }
}
