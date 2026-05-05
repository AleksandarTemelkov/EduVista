from score_scale       import ScoreScale
from entries_extractor import Entry, EntryType, Entries, EntriesCategory, StatCategory
from functools         import cached_property

# Analyzer Class
"""Main class to analyze statistics from PDF entries."""
class StatisticsAnalyzer:
    def __init__(self, score_scale: ScoreScale, entries: list[Entry]) -> None:
        # Entries & Scores
        self.entries_all      = Entries(entries, lambda e: e.entry_type == EntryType.SCORE or e.entry_type == EntryType.ABSENT)
        self.entries_positive = Entries(entries, lambda e: e.entry_type == EntryType.SCORE and e.value >= score_scale.passing_threshold)
        self.entries_negative = Entries(entries, lambda e: e.entry_type == EntryType.SCORE and e.value < score_scale.passing_threshold)
        self.entries_absent   = Entries(entries, lambda e: e.entry_type == EntryType.ABSENT)

        # Caches
        self._percentile_cache = {}
    
    # The below methods are now replaced by cached properties, so they will be calculated on demand and cached for future use.
    #
    # def count_absent(self) -> None:
    #     """Counts the number of absent entries."""
    #     self.absent_count = sum(
    #         1 for entry in self.entries_all.entries 
    #             if entry.entry_type == EntryType.ABSENT
    #     )
    # 
    #     self.absent_counted = True
    #
    # @staticmethod
    # def _object_check(obj, calculation_method: Callable[[], None]) -> None:
    #     """Checks if an object is None, calls calculation method if it is."""
    #     if not obj: calculation_method()
    # 
    # def _scores_extracted_check(self) -> None:
    #     """Checks if the scores have been extracted."""
    #     self._object_check(self.scores, self.extract_scores)
    # 
    # def _absent_counted_check(self) -> None:
    #     """Checks if the absent count has been calculated."""
    #     self._object_check(self.absent_count, self.count_absent)
    
    # Entries & Scores
    def extract_scores(self) -> None:
        """Extracts scores from the entries and stores them in a list."""
        self.scores = [
            entry.value for entry in self.entries_all.entries
                if entry.entry_type == EntryType.SCORE
        ]
        self.scores = sorted(self.scores)  # Sort scores for median and percentile calculations
        
        self.scores_extracted = True

    @cached_property
    def scores(self) -> list[float]:
        """Returns the list of scores, extracting them if necessary."""
        return self.extract_scores() or self.scores


    # Basic Stats
    @cached_property
    def total_count(self) -> int:
        return self.entries_all.len() if self.entries_all else 0
    
    @cached_property
    def absent_count(self) -> int:
        return self.entries_absent.len() if self.entries_absent else 0
    
    @cached_property
    def positive_scores_count(self) -> int:
        return self.entries_positive.len() if self.entries_positive else 0
    
    @cached_property
    def negative_scores_count(self) -> int:
        return self.entries_negative.len() if self.entries_negative else 0
    
    @cached_property
    def scores_count(self) -> int:
        return len(self.scores) if self.scores else 0

    @cached_property
    def min_score(self) -> float:
        return min(self.scores) if self.scores else float('inf')

    @cached_property
    def max_score(self) -> float:
        return max(self.scores) if self.scores else float('-inf')

    @cached_property
    def pass_rate_total(self) -> float:
        return self.positive_scores_count / self.total_count if self.entries_positive and self.entries_all else 0
    
    @cached_property
    def pass_rate_present(self) -> float:
        return self.positive_scores_count / (self.total_count - self.absent_count) if self.entries_positive and self.entries_all else 0


    # Calculations
    @cached_property
    def mean(self) -> float:
        """Calculates the mean score using an incremental approach to avoid potential overflow issues with large datasets."""
        if not self.scores: return None

        mean_score = 0
        for n, value in enumerate(self.scores, start = 1):
            if (n == 1):
                mean_score = value
                continue
            
            mean_score = ((mean_score * (n - 1)) + value) / n
        
        return mean_score

    @cached_property
    def median(self) -> float:
        """Calculates the median score by sorting the scores and finding the middle value(s)."""
        if not self.scores: return None
        
        mid = self.scores_count // 2

        if self.scores_count % 2 == 0:  return (self.scores[mid - 1] + self.scores[mid]) / 2
        else:                           return self.scores[mid]

    @cached_property
    def mode(self) -> float:
        """Calculates the mode score by counting the frequency of each score and returning the most common one."""
        if not self.scores: return None
        
        frequency = {}
        for item in self.scores:
            frequency[item] = frequency.get(item, 0) + 1
        mode = max(frequency, key = frequency.get)

        return mode
    
    @cached_property
    def range(self) -> float:
        """Calculates the range of scores."""
        if not self.scores: return None
        
        return self.max_score - self.min_score
    
    @cached_property
    def stddev(self) -> float:
        """Calculates standard deviation of scores."""
        if not self.scores or self.scores_count < 2: return None

        mu = self.mean

        variance = sum((x - mu) ** 2 for x in self.scores) / (self.scores_count - 1)
        return variance ** 0.5
    
    @cached_property
    def cov(self) -> float:
        """Calculates coefficient of variance of scores."""
        if not self.scores or self.scores_count < 2 or self.mean == 0: return None
        return self.stddev / self.mean
    
    def scores_count_in_sigma_interval(self, i: int) -> int:
        """Counts how many scores fall within i standard deviations from the mean."""

        def scores_sigma_interval(i: int) -> tuple[float, float]:
            """Returns the interval of scores within i standard deviations from the mean."""
            return (self.mean - i * self.stddev, self.mean + i * self.stddev)
    
        lower, upper = scores_sigma_interval(i)
        return sum(1 for score in self.scores if lower <= score <= upper)
    
    def scores_percentage_in_sigma_interval(self, i: int) -> float:
        """Calculates the percentage of scores that fall within i standard deviations from the mean."""
        if self.scores_count == 0: return 0
        
        count_in_interval = self.scores_count_in_sigma_interval(i)
        return (count_in_interval / self.scores_count) * 100
    
    @cached_property
    def skewness(self) -> float:
        """Calculates skewness of scores using Pearson's Moment Coefficient of Skewness."""
        if not self.scores or self.scores_count < 3 or self.stddev == 0: return None

        mu = self.mean
        sigma = self.stddev
        
        # Pearson's Moment Coefficient of Skewness
        m3 = sum((x - mu) ** 3 for x in self.scores) / self.scores_count
        return m3 / (sigma ** 3)
    
    def calculate_percentile(self, p: float) -> float:
        """Calculates any custom percentile (0-100)."""
        if p not in self._percentile_cache:
            if not self.scores: return 0
            index = (p / 100) * (self.scores_count - 1)
            
            # Linear interpolation if the index isn't a whole number
            lower = self.scores[int(index)]
            upper = self.scores[int(index) + 1] if int(index) + 1 < self.scores_count else lower
            value = lower + (upper - lower) * (index % 1)
            self._percentile_cache[p] = value
        
        return self._percentile_cache[p]


    # String Methods
    def attr_str(self, attr_category) -> str:
        """Returns a string representation of the specified attribute category."""
        if isinstance(attr_category, EntriesCategory):
            attr_name: str = attr_category.value
            entries_obj = getattr(self, attr_name)
            return f"{attr_name} = {entries_obj.toString()}"
        elif isinstance(attr_category, StatCategory):
            attr_name: str = attr_category.value
            stat_value = getattr(self, attr_name)
            return f"{attr_name} = {stat_value}"
        else:
            attr_name: str = str(attr_category)
            attr_value = getattr(self, attr_name, None)
            return f"{attr_name} = {attr_value}"
        
    def str_entries_all(self) -> str:      return self.attr_str(EntriesCategory.ALL)
    def str_entries_positive(self) -> str: return self.attr_str(EntriesCategory.POSITIVE)
    def str_entries_negative(self) -> str: return self.attr_str(EntriesCategory.NEGATIVE)
    def str_entries_absent(self) -> str:   return self.attr_str(EntriesCategory.ABSENT)
    

    # Prints
    def print_attr(self, attr_category):
        """Prints the specified entries category."""
        if isinstance(attr_category, EntriesCategory):
            attr_name: str = attr_category.value
            entries_obj = getattr(self, attr_name)
            
            print(f"{attr_name} = ", end="")
            entries_obj.print()
        elif isinstance(attr_category, StatCategory):
            attr_name: str = attr_category.value
            stat_value = getattr(self, attr_name)
            print(f"{attr_name} =", stat_value)
        else:
            attr_name: str = str(attr_category)
            attr_value = getattr(self, attr_name, None)
            print(f"{attr_name} =", attr_value)
    
    def print_entries_all(self) -> None:      self.print_attr(EntriesCategory.ALL)
    def print_entries_positive(self) -> None: self.print_attr(EntriesCategory.POSITIVE)
    def print_entries_negative(self) -> None: self.print_attr(EntriesCategory.NEGATIVE)
    def print_entries_absent(self) -> None:   self.print_attr(EntriesCategory.ABSENT)

    def print_mean(self) -> None:             self.print_attr(StatCategory.MEAN)
    def print_median(self) -> None:           self.print_attr(StatCategory.MEDIAN)
    def print_mode(self) -> None:             self.print_attr(StatCategory.MODE)
    def print_range(self) -> None:            self.print_attr(StatCategory.RANGE)
    def print_stddev(self) -> None:           self.print_attr(StatCategory.STDDEV)
    def print_skewness(self) -> None:         self.print_attr(StatCategory.SKEWNESS)
    def print_percentile(self, percentile: float) -> None: 
        print(f"percentile_{percentile} =", self.calculate_percentile(percentile))

    def print_scores(self) -> None:
        """Prints the list of scores."""
        print("scores = [", end="")
        for i, score in enumerate(self.scores):
            print(score, end = "")
            if (i != self.scores_count - 1): print(", ", end = "")
        print("]")
    
    def print_score_min(self) -> None:
        """Prints the minimum score."""
        print("score_min =", self.score_min)

    def print_score_max(self) -> None:
        """Prints the maximum score."""
        print("score_max =", self.score_max)

    def print_scores_count(self) -> None:
        """Prints the count of scores."""
        print("scores_count =", self.scores_count)

    def print_absent_count(self) -> None:
        """Prints the count of absent entries."""
        print("absent_count =", self.absent_count)
    
    def print_pass_rate(self) -> None:
        """Prints the pass rate."""
        print("pass_rate =", self.pass_rate)

