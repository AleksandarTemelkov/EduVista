from assessments           import Assessments
from entries_extractor     import EntriesExtractor
from statistics_analyzer   import StatisticsAnalyzer
from statistics_visualizer import StatisticsVisualizer
from terminal_silencer     import TerminalSilencer
import argparse


# Debug Flags
debugEntries: bool = False
debugStats: bool = False

# Separators
SEP_LENGTH = 128
sep_major = "=" * SEP_LENGTH
sep_minor = "–" * SEP_LENGTH

# Terminal Silencer instancing
silencer = TerminalSilencer()


if __name__ == "__main__":
    print(sep_major)

    parser = argparse.ArgumentParser()
    parser.add_argument("--assessment", required=True, 
        help="Format: SP_K1_2026")

    args = parser.parse_args()
    
    # Dynamically resolve from Assessments enum
    try:
        entered_assessment: str = args.assessment
        current_assessment = getattr(Assessments, entered_assessment.upper())
    except AttributeError:
        print(f"[ERROR] Assessment '{entered_assessment}' not found in available assessments.")
        print(sep_minor)

        print("Available assessments:")
        for assessment in Assessments:
            print(f"• {assessment.name}")
        
        print(sep_major)
        exit(1)
    except Exception as e:
        print(e)
        print(sep_major)
        exit(1)
    
    # Get the specific scale and layout
    active_scale = current_assessment.get_score_scale()
    active_layout = current_assessment.layout

    # Extraction
    extractor = EntriesExtractor(active_layout, active_scale)
    input_file = f"./input/{current_assessment.get_filename()}.pdf"
    keyboardInterrupt = False

    try:
        silencer.enable_silent_mode()  # This hides ^C
        scores = extractor.extract_pdf(input_file)
        analyzer = StatisticsAnalyzer(active_scale, scores)

        if debugEntries:
            print(sep_major)
            print("ENTRIES:")
            print(sep_minor)
            analyzer.print_scores()
            print()
            analyzer.print_entries_positive()
            print()
            analyzer.print_entries_negative()
            print()
            analyzer.print_entries_absent()
            print(sep_major)

        if debugStats:
            print(sep_major)
            print("STATISTICS:")
            print(sep_minor)
            analyzer.print_score_min()
            analyzer.print_score_max()
            analyzer.print_scores_count()
            analyzer.print_absent_count()
            analyzer.print_pass_rate()
            analyzer.print_mean()
            analyzer.print_median()
            analyzer.print_mode()
            analyzer.print_range()
            analyzer.print_stddev()
            analyzer.print_skewness()
            analyzer.print_percentile(25)
            analyzer.print_percentile(50)
            analyzer.print_percentile(75)
            print(sep_major)
        
        # Visualization
        visualizer = StatisticsVisualizer(current_assessment, analyzer)
        visualizer.graph_scores()
        
    except (KeyboardInterrupt):
        keyboardInterrupt = True

    except Exception as e:
        print(e)
        print(sep_major)
        exit(1)

    finally:
        silencer.restore() # Restore the original state


    print(sep_minor)
    print("[INFO] Analysis completed successfully.")
    print(sep_major)