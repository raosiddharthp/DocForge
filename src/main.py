import sys
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.parsing.code_parser import CodeParser
from src.parsing.doc_parser import DocParser
from src.core.drift import DriftAnalyzer
from src.core.graph import app as logic_swarm
from src.core.state import AgentState

console = Console()

def main():
    parser = argparse.ArgumentParser(description="DocForge: Shift-Left Documentation Engine")
    parser.add_argument("file", help="The source code file to audit (e.g., api.py)")
    parser.add_argument("--spec", help="The requirement spec file (e.g., prd.md)", default=None)
    args = parser.parse_args()

    target_file = args.file
    spec_file = args.spec
    
    # --- Phase 1: Structural Analysis ---
    console.rule("[bold blue]Phase 1: Structural Analysis")
    
    # 1. Parse Code
    try:
        code_parser = CodeParser()
        code_entities = code_parser.parse_file(target_file)
        console.print(f"✅ Parsed {len(code_entities)} interface contracts from [cyan]{target_file}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]Error parsing code:[/bold red] {e}")
        sys.exit(1)

    # 2. Parse Spec (If provided) & Detect Drift
    doc_requirements = []
    drift_report = None
    
    if spec_file:
        try:
            doc_parser = DocParser()
            doc_requirements = doc_parser.parse_file(spec_file)
            console.print(f"✅ Parsed {len(doc_requirements)} requirements from [cyan]{spec_file}[/cyan]")
            
            # Run Drift Analysis
            analyzer = DriftAnalyzer()
            drift_report = analyzer.analyze(code_entities, doc_requirements)
            
            # Display Drift Report
            table = Table(title="Drift Analysis Report")
            table.add_column("Requirement", style="cyan")
            table.add_column("Code Match", style="magenta")
            table.add_column("Status", style="bold")

            # Show Linked items
            for pair in drift_report.entity_pairs:
                table.add_row(pair['doc_title'], pair['code_name'], "[green]LINKED[/green]")
            
            # Show Missing Items (Drift)
            critical_drift = False
            for doc in drift_report.orphaned_docs:
                if doc.importance == 'must':
                    table.add_row(doc.section_title, "MISSING", "[red]CRITICAL DRIFT[/red]")
                    critical_drift = True
                else:
                    table.add_row(doc.section_title, "MISSING", "[yellow]WARNING[/yellow]")

            console.print(table)
            
            if critical_drift:
                console.print("\n[bold red]⛔ COMMIT BLOCKED: Critical requirements missing in code.[/bold red]")
                sys.exit(1)

        except Exception as e:
            console.print(f"[bold red]Error parsing spec:[/bold red] {e}")
            sys.exit(1)

    # --- Phase 2: Agentic Generation ---
    console.rule("[bold blue]Phase 2: Agentic Documentation")
    
    all_passed = True
    
    for entity in code_entities:
        console.print(f"\n[bold yellow]Processing: {entity.name}[/bold yellow]")
        
        # Initialize State for this function
        state = AgentState(
            project_name="CLI Run",
            target_file=target_file,
            code_context=[entity], 
            doc_requirements=doc_requirements, # Pass requirements to agents
            drift_report=drift_report.model_dump() if drift_report else {},
            critique_count=0,
            max_revisions=3,
            current_draft="",
            critique_feedback=None,
            is_compliant=False
        )

        # Run the Swarm
        final_state = logic_swarm.invoke(state)
        
        if final_state['is_compliant']:
            status = "[green]APPROVED[/green]"
            border = "green"
        else:
            status = "[red]NON-COMPLIANT (Max Retries)[/red]"
            border = "red"
            all_passed = False

        console.print(Panel(
            final_state['current_draft'],
            title=f"{entity.name} - {status}",
            border_style=border
        ))

    # Final Exit Code
    if not all_passed:
        console.print("\n[bold red]⛔ COMMIT BLOCKED: Style violations detected.[/bold red]")
        sys.exit(1)
    else:
        console.print("\n[bold green]✨ DocForge Audit Passed.[/bold green]")

if __name__ == "__main__":
    main()