# Documentation

Working documents from a 24-hour hackathon build, kept for provenance. The
project itself is described in the [root README](../README.md).

### Design and architecture

| Document | Contents |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture: the three-layer orchestration design, data flow, and component responsibilities |
| [RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md) | Research into serverless architecture options, with the reasoning behind the stack that was chosen |
| [PLAN.md](PLAN.md) | Backend implementation plan |
| [gemini.md](gemini.md) | Project map and the response schema for every external API the tools consume |

### Agent orchestration

The platform is driven by an LLM orchestration layer, so its behaviour is
specified in prose rather than code. These are those specifications.

| Document | Contents |
|---|---|
| [MASTER_ORCHESTRATION.md](MASTER_ORCHESTRATION.md) | Top-level orchestration entry point |
| [Agents.md](Agents.md) | Agent instructions |
| [BLAST.md](BLAST.md) / [BLAST_INSTANTIATED.md](BLAST_INSTANTIATED.md) | The B.L.A.S.T. working method, and the instantiated version for this build |
| [schools_ofsted_fetcher.md](schools_ofsted_fetcher.md) | Directive for the schools and Ofsted worker |
| [video_explainer_generation.md](video_explainer_generation.md) | Directive for the video report generator |

The executable directives the running system reads are in
[`directives/`](../directives/); the copies here are earlier drafts that
diverged.

### Build log and presentation

| Document | Contents |
|---|---|
| [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md), [SETUP_COMPLETE.md](SETUP_COMPLETE.md) | Progress checkpoints written during the build |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md), [CHEAT_SHEET.md](CHEAT_SHEET.md) | Working notes and the pitch cheat sheet |
| [PRESENTATION.md](PRESENTATION.md) | Presentation script |
| [Claude_updated.md](Claude_updated.md) | Session notes |
