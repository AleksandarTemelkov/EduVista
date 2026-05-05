from assessments          import Assessment
from statistics_analyzer  import StatisticsAnalyzer
from scipy.stats          import norm   # pyright: ignore[reportMissingImports]
from tkinter import messagebox
import matplotlib.pyplot  as plt        # pyright: ignore[reportMissingModuleSource]
import seaborn            as sns        # pyright: ignore[reportMissingModuleSource]
import numpy              as np         # pyright: ignore[reportMissingImports]
import pathlib

class StatisticsVisualizer:
    def __init__(self, assessment: Assessment, analyzer: StatisticsAnalyzer) -> None:
        # Store the core objects
        self.assessment = assessment
        self.analyzer = analyzer
        
        # Extract specific visualization data from the assessment
        # This automatically picks 35% for Midterm or 50% for Exam scale
        self.score_scale = assessment.get_score_scale() 
        
        # Use the helper methods we defined in the Assessment class
        self.title = assessment.get_title()
        self.filename = assessment.get_filename()
        
        # Access subject-specific styling
        self.color = assessment.subject.color

    @staticmethod
    def _get_bins_v1(x_min, x_max, resolution = 5):
        """
        Creates bins that snap to the 'resolution' (e.g., 1, 5, 10).
        """
        # Floor to nearest multiple of resolution
        # Example: 27 // 5 = 5 -> 5 * 5 = 25 (Starts @ 25)
        start = (int(x_min) // resolution) * resolution
        
        # Ceil to nearest multiple of resolution
        # Example: 92 / 5 = 18.4 -> 19 * 5 = 95 (Ends @ 95)
        end = np.ceil(x_max / resolution) * resolution
        
        # Add resolution to include the upper bound
        return np.arange(start, end + resolution, resolution)
    
    def _get_bins_v2(self, method='grade'):
        """
        Auto-select bins based on statistical best practices.
        
        Args:
            scores: Array of score data
            method: 'fd' (Freedman-Diaconis), 'sturges', 'sqrt', or 'grade'
        """
        n         = self.analyzer.scores_count 
        min_score = self.analyzer.min_score
        max_score = self.analyzer.max_score
        
        if method == 'fd':
            # Freedman-Diaconis (robust, handles outliers)
            q25 = self.analyzer.calculate_percentile(25)
            q75 = self.analyzer.calculate_percentile(75)
            iqr = q75 - q25
            bin_width = 2 * iqr / (n ** (1/3))
            bins = np.arange(min_score, max_score + bin_width, bin_width)
            
        elif method == 'sturges':
            # Sturges' rule (good for normal-ish data)
            bins = int(np.ceil(np.log2(n) + 1))
            
        elif method == 'sqrt':
            # Square root rule (simple baseline)
            bins = int(np.ceil(np.sqrt(n)))
            
        elif method == 'grade':
            # Educational: 5-point bins
            bin_width = 1
            start = np.floor(min_score / bin_width) * bin_width
            end = np.ceil(max_score / bin_width) * bin_width
            bins = np.arange(start, end + bin_width, bin_width)
            
        return bins
    
    def _get_bins(self):
        """Smart bin selection."""
        min_score = self.analyzer.min_score
        max_score = self.analyzer.max_score
        point = 1
        
        # If scores span a narrow range (<25 points), use 1-point bins
        if max_score - min_score < 20:
            return np.arange(min_score, max_score + 1, point)
        
        # If scores span wide range (>75 points), use 7-point bins
        elif max_score - min_score > 60:
            point = 7
            return np.arange(min_score, max_score + 1, point)
        
        # Default: 3-point bins for typical 25–75 point ranges
        else:
            point = 3
            start = np.floor(min_score / point) * point
            end = np.ceil(max_score / point) * point
            return np.arange(start, end + point, point)

    def _get_save_path(self) -> str:
        # Setup path: Project_Root/graphs/
        # This finds the directory where your script is located
        base_dir = pathlib.Path(__file__).parent.resolve()
        save_dir = base_dir / "graphs"
        save_dir.mkdir(exist_ok=True) # Creates folder if missing

        # Use the logic-based filename instead of the title
        extension = ".png"
        main_path = save_dir / f"{self.filename}{extension}"
        
        if main_path.exists():
            # Find the next available version number
            counter = 1
            while (save_dir / f"{self.filename}-v{counter}{extension}").exists():
                counter += 1
        
            # Rename existing file: graph.png -> graph-v{counter}.png
            old_version_path = save_dir / f"{self.filename}-v{counter}{extension}"
            main_path.rename(old_version_path)

        # Always return the 'main' path for the new save
        return str(main_path)

    def graph_scores(self) -> None:
        """Main function for graphing scores."""
        # Unbind the default 's' (save)
        plt.rcParams['keymap.save'] = []

        # Create figure and histogram
        fig, ax_hist = plt.subplots(1, figsize=(16, 8))
        fig.canvas.manager.set_window_title(self.title)
        ax_hist.set_title(self.title)
        ax_hist.set_xlabel("Odstotek rezultata (%)")
        ax_hist.set_ylabel("Število prisotnih (n)")

        # Define the save function
        def on_key(event):
            if event.key == 's':
                path = self._get_save_path()
                fig.savefig(path, dpi=300, bbox_inches='tight')
                print(f"💾 Grafikon uspešno shranjen: {path}")

        # Connect the event to the figure
        fig.canvas.mpl_connect('key_press_event', on_key)


        # Stats and Limits
        mu = self.analyzer.mean
        sd = self.analyzer.stddev
        md = self.analyzer.median
        mo = self.analyzer.mode
        s_min_scale, s_max_scale = self.score_scale.score_min, self.score_scale.score_max
        s_min_data, s_max_data = self.analyzer.min_score, self.analyzer.max_score

        def calculate_sigma_limits():
            """Returns least integer sigma coverage needed to encompass all data."""
            if sd > 0:
                dist_min = (mu - s_min_data) / sd
                dist_max = (s_max_data - mu) / sd
                return dist_min, dist_max
            return 1, 1
        
        sigma_low, sigma_high = calculate_sigma_limits()

        # Define plot range clamped to the scale (0-100)
        def round_to_5(x): return round(x / 5.0) * 5
        x_min = max(s_min_scale, round_to_5(mu - sigma_low  * sd) - 5)
        x_max = min(s_max_scale, round_to_5(mu + sigma_high * sd) + 5)
        x_full = np.linspace(x_min, x_max, 500)
        # x_full = self._get_optimized_bins(x_min, x_max)


        # Define the Curve Axis (This will be the background layer)
        # We rename ax_hist to ax_curve conceptually or just use ax_hist
        ax_curve = ax_hist

        # Draw Curve Background (on the primary ax_hist)
        # We need a temporary histogram call just to find the max 'count' for scaling
        # counts, _ = np.histogram(self.analyzer.scores, bins=int(x_max-x_min), range=(x_min, x_max))
        # max_height = max(counts) if len(counts) > 0 else 1
        # plot_limit = np.ceil(max_height) + 1
        
        # ax_curve.set_ylim(0, plot_limit)
        # y_peak = norm.pdf(mu, mu, sd) if sd > 0 else 1
        # y_full = norm.pdf(x_full, mu, sd) * (max_height / y_peak)

        # ...


        # resolution: int = 5
        # bins = self._get_bins_v1(self.analyzer.min_score, self.analyzer.max_score, resolution)
        bins = self._get_bins()

        # Calculate histogram counts with your actual bins
        counts, bin_edges = np.histogram(self.analyzer.scores, bins=bins)
        max_height = max(counts) if len(counts) > 0 else 1

        # Set y-limit (tallest bin + 1 for visual padding)
        y_limit = max_height + 1
        ax_curve.set_ylim(0, y_limit)
        plot_limit = y_limit  # Store for reference

        # Scale the normal curve to match the histogram height
        if sd > 0:
            y_peak = norm.pdf(mu, mu, sd)
            y_full = norm.pdf(x_full, mu, sd) * (max_height / y_peak)
        else:
            y_full = np.zeros_like(x_full)

        # Draw Bars (on twin axis to ensure they are on TOP)
        ax_bars = ax_hist.twinx()
        sns.histplot(
            self.analyzer.scores,
            ax=ax_bars,
            bins=bins,  # Custom bins instead of binwidth/binrange
            # binwidth=1.0,
            # binrange=(np.floor(x_min) - 0.5, np.ceil(x_max) - 0.5),
            stat="count",
            kde=False, 
            color="black",
            edgecolor="white", 
            linewidth=1,
            alpha=0.7,
            zorder=5
        )
        ax_bars.set_ylim(0, plot_limit)
        ax_bars.get_yaxis().set_visible(False) # Only use ax_hist y-axis


        # BELL CURVE

        # Sigma Band Function
        def add_sigma_band(sigma_level, color, alpha, label):
            if sd <= 0: return
            
            # We define the inner boundary to "hollow out" the larger bands
            inner = sigma_level - 1
            
            if sigma_level == 1:
                # The core: everything from -1σ to +1σ
                mask = (x_full >= mu - sd) & (x_full <= mu + sd)
                ax_curve.fill_between(x_full[mask], 0, y_full[mask], color=color, alpha=alpha, linewidth=0, label=label)
            else:
                # The "Wings": only the area between (level-1) and (level)
                mask_left  = ((x_full >= mu - sigma_level * sd) & (x_full <= mu - inner * sd))
                mask_right = ((x_full >= mu + inner * sd) & (x_full <= mu + sigma_level * sd))
            
                ax_curve.fill_between(x_full[mask_left ], 0, y_full[mask_left ], color=color, alpha=alpha, linewidth=0)
                ax_curve.fill_between(x_full[mask_right], 0, y_full[mask_right], color=color, alpha=alpha, linewidth=0, label=label)

        # Standard deviation bands
        num_sd_bands = 3
        range_sd_bands = range(1, num_sd_bands + 1)
        alphas = [1.0 / i for i in range_sd_bands]
        
        for i, alpha in zip(range_sd_bands, alphas):
            pct = self.analyzer.scores_percentage_in_sigma_interval(i)
            add_sigma_band(i, self.color, alpha, f"{i}σ ({pct:.2f}%)")

        # The "Bell Curve" outline
        # ax_curve.plot(x_full, y_full, color=self.color, linewidth=2, linestyle='-', alpha=0.5, zorder=1.5)


        # Statistical Lines (zorder=3, sitting on top of everything)
        ax_hist.axvline(mu, color='red',    linewidth=2, label=f'Povprečje: {mu:.2f}', zorder=3)
        ax_hist.axvline(md, color='green',  linewidth=2, label=f'Mediana: {self.analyzer.median:.2f}', zorder=3)
        ax_hist.axvline(mo, color='purple', linewidth=2, label=f'Modus: {self.analyzer.mode:.2f}', zorder=3)
        
        # Percentiles
        p25, p75 = self.analyzer.calculate_percentile(25), self.analyzer.calculate_percentile(75)
        ax_hist.axvline(p25, color='blue', linestyle='--', label='25. percentil', zorder=3)
        ax_hist.axvline(p75, color='blue', linestyle='--', label='75. percentil', zorder=3)


        # Grid and Ticks
        ax_hist.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax_hist.xaxis.grid(True, linestyle='--', alpha=0.25, color='gray', zorder=0)
        ax_hist.yaxis.grid(True, linestyle='--', alpha=0.25, color='gray', zorder=0)
        ax_hist.set_xlim(x_min, x_max)
        tick_start = int(np.floor(x_min))
        tick_end   = int(np.ceil(x_max)) + 1
        ax_hist.set_xticks(range(tick_start, tick_end, 5))
        ax_hist.tick_params(labelbottom=True)

        # Final Legend and Text
        h_curve, l_curve = ax_curve.get_legend_handles_labels()
        h_bars, l_bars = ax_bars.get_legend_handles_labels()
        ax_curve.legend(h_bars + h_curve, l_bars + l_curve, loc='upper left', bbox_to_anchor=(1, 1), frameon=True)
        

        # Other Stats
        stats_separator: str = '–' * 32
        stats_text = (
            f"• Skupaj študentov: {self.analyzer.total_count}\n"
            f"• Skupaj prisotnih: {self.analyzer.scores_count}\n"
            f"  • Skupaj pozitivnih: {self.analyzer.positive_scores_count}\n"
            f"  • Skupaj negativnih: {self.analyzer.negative_scores_count}\n"
            f"• Skupaj odsotnih:  {self.analyzer.absent_count}\n"
            f"{stats_separator}\n"
            f"• Skupna uspešnost: {self.analyzer.pass_rate_total * 100:.2f}%\n"
            f"• Uspešnost prisotnih: {self.analyzer.pass_rate_present * 100:.2f}%\n"
            f"{stats_separator}\n"
            f"• Min–Max:         {self.analyzer.min_score}–{self.analyzer.max_score}\n"
            f"• Obseg:           {self.analyzer.range:.2f}\n"
            f"• Std. odklon:     {self.analyzer.stddev:.2f}\n"
            f"• Koef. variacije: {self.analyzer.cov * 100:.2f}%\n"
            f"• Poševnost:       {self.analyzer.skewness:.2f}"
        )

        props = dict(boxstyle = 'round', facecolor = 'white', alpha = 0.5, linewidth = 1, edgecolor = 'gray')
        ax_hist.text(
            1.01, 0.02,
            stats_text, 
            bbox = props, 
            transform = ax_hist.transAxes, 
            verticalalignment = 'bottom', 
            horizontalalignment = 'left',
            fontfamily = 'monospace',
            fontsize = 10,
        )

        plt.tight_layout()
        print("💡 Press 's' on the keyboard to save the plot.")
        plt.show()