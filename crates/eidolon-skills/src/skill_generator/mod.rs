pub mod generator;

pub use generator::*;

pub fn detect_reusable_patterns(interactions: &[String]) -> Vec<Pattern> {
    SkillGenerator::detect_patterns(interactions)
}

pub fn template_for_pattern(pattern: &Pattern) -> String {
    SkillGenerator::generate_skill_template(pattern)
}
