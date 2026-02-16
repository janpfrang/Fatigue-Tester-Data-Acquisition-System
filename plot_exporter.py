"""
Plot Exporter Module
Handles exporting plots to PDF and other formats

Part of Phase 2 refactoring - NEW FEATURE: PDF Export
"""

import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
from typing import Optional
import numpy as np


class PlotExporter:
    """
    Export plots to various formats (PDF, PNG)
    Generates publication-quality plots from live data
    """
    
    def __init__(self, plotter):
        """
        Initialize plot exporter
        
        Args:
            plotter: LivePlotter instance with data buffers
        """
        self.plotter = plotter
    
    def export_to_pdf(self, filepath: str, 
                     include_metadata: bool = True,
                     threshold_monitor=None,
                     statistics_tracker=None,
                     log_filename=None) -> bool:
        """
        Export all plots to a multi-page PDF
        
        Args:
            filepath: Output PDF file path
            include_metadata: Include test metadata on first page
            threshold_monitor: Optional ThresholdMonitor for violation info
            statistics_tracker: Optional StatisticsTracker for test info
            log_filename: Optional log filename to include in metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get data from plotter
            cycles = list(self.plotter.cycles)
            force_lower = list(self.plotter.force_lower)
            force_upper = list(self.plotter.force_upper)
            travel_1 = list(self.plotter.travel_1)
            travel_2 = list(self.plotter.travel_2)
            travel_at_upper = list(self.plotter.travel_at_upper)
            loss_of_stiffness = list(self.plotter.loss_of_stiffness)
            
            if not cycles:
                return False
            
            # Create PDF
            with PdfPages(filepath) as pdf:
                
                # Page 1: All Three Plots on One Page
                fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 14))
                fig.suptitle('Fatigue Test Results - All Plots', fontsize=16, fontweight='bold', y=0.995)
                
                # Plot 1: Forces vs Cycles
                ax1.plot(cycles, force_lower, 'b-', linewidth=1.5, label='Lower Force [N]')
                ax1.plot(cycles, force_upper, 'r-', linewidth=1.5, label='Upper Force [N]')
                
                # Add threshold lines if enabled
                if threshold_monitor and threshold_monitor.config.upper_force_enabled:
                    ax1.axhline(y=threshold_monitor.config.upper_force_upper_limit, 
                               color='orange', linestyle='--', linewidth=1, 
                               label=f'Upper Limit: {threshold_monitor.config.upper_force_upper_limit:.1f} N')
                    ax1.axhline(y=threshold_monitor.config.upper_force_lower_limit, 
                               color='orange', linestyle='--', linewidth=1,
                               label=f'Lower Limit: {threshold_monitor.config.upper_force_lower_limit:.1f} N')
                
                ax1.set_xlabel('Cycles', fontsize=11)
                ax1.set_ylabel('Force [N]', fontsize=11)
                ax1.set_title('Forces vs Cycles', fontsize=12, fontweight='bold')
                ax1.grid(True, alpha=0.3)
                ax1.legend(loc='best', fontsize=9)
                
                # Add violation info if available
                if threshold_monitor and threshold_monitor.config.upper_force_enabled:
                    violation_text = f'Violations: {threshold_monitor.force_violations}'
                    ax1.text(0.02, 0.98, violation_text, transform=ax1.transAxes,
                            verticalalignment='top', fontsize=9,
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                
                # Plot 2: Travel Measurements vs Cycles
                ax2.plot(cycles, travel_at_upper, 'g-', linewidth=1.5, label='Travel at Upper [mm]')
                ax2.plot(cycles, travel_1, 'c-', linewidth=1, label='Travel 1 [mm]', alpha=0.7)
                ax2.plot(cycles, travel_2, 'm-', linewidth=1, label='Travel 2 [mm]', alpha=0.7)
                
                ax2.set_xlabel('Cycles', fontsize=11)
                ax2.set_ylabel('Travel [mm]', fontsize=11)
                ax2.set_title('Travel Measurements vs Cycles', fontsize=12, fontweight='bold')
                ax2.grid(True, alpha=0.3)
                ax2.legend(loc='best', fontsize=9)
                
                # Plot 3: Loss of Stiffness vs Cycles
                ax3.plot(cycles, loss_of_stiffness, 'orange', linewidth=1.5, 
                        label='Loss of Stiffness [%]')
                
                # Add threshold lines if enabled
                if threshold_monitor and threshold_monitor.config.stiffness_enabled:
                    ax3.axhline(y=threshold_monitor.config.stiffness_upper_limit, 
                               color='red', linestyle='--', linewidth=1,
                               label=f'Upper Limit: {threshold_monitor.config.stiffness_upper_limit:.1f} %')
                    ax3.axhline(y=threshold_monitor.config.stiffness_lower_limit, 
                               color='red', linestyle='--', linewidth=1,
                               label=f'Lower Limit: {threshold_monitor.config.stiffness_lower_limit:.1f} %')
                
                ax3.set_xlabel('Cycles', fontsize=11)
                ax3.set_ylabel('Loss of Stiffness [%]', fontsize=11)
                ax3.set_title('Loss of Stiffness vs Cycles', fontsize=12, fontweight='bold')
                ax3.grid(True, alpha=0.3)
                ax3.legend(loc='best', fontsize=9)
                
                # Add violation info if available
                if threshold_monitor and threshold_monitor.config.stiffness_enabled:
                    violation_text = f'Violations: {threshold_monitor.stiffness_violations}'
                    ax3.text(0.02, 0.98, violation_text, transform=ax3.transAxes,
                            verticalalignment='top', fontsize=9,
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                
                # Adjust layout to prevent overlap
                plt.tight_layout(rect=[0, 0, 1, 0.99])
                
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
                
                # Page 2: Summary/Metadata (if requested)
                if include_metadata:
                    fig4, ax4 = plt.subplots(figsize=(11, 8.5))
                    ax4.axis('off')
                    
                    # Build metadata text
                    metadata_lines = [
                        'Fatigue Test Summary Report',
                        '=' * 70,
                        '',
                        f'Export Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                        f'Total Cycles: {len(cycles)}',
                        ''
                    ]
                    
                    # Add log filename if provided
                    if log_filename:
                        metadata_lines.extend([
                            'Data Log File:',
                            '-' * 70,
                            f'{log_filename}',
                            ''
                        ])
                    
                    if statistics_tracker:
                        stats = statistics_tracker.get_summary()
                        metadata_lines.extend([
                            'Test Statistics:',
                            '-' * 70,
                            f'Data Points: {stats["data_points"]}',
                            f'Test Duration: {stats["connection_duration"]:.1f} seconds',
                            f'Data Rate: {stats["data_rate"]:.2f} points/second',
                            f'Lines Parsed: {stats["lines_parsed"]}',
                            f'Lines Skipped: {stats["lines_skipped"]} (headers/config)',
                            ''
                        ])
                    
                    if threshold_monitor:
                        threshold_stats = threshold_monitor.get_statistics()
                        metadata_lines.extend([
                            'Threshold Monitoring:',
                            '-' * 70,
                        ])
                        
                        if threshold_stats['force_enabled']:
                            force_pct = (threshold_stats["force_violations"] / len(cycles) * 100) if len(cycles) > 0 else 0
                            metadata_lines.extend([
                                f'Upper Force Thresholds: ENABLED',
                                f'  Upper Limit: {threshold_stats["force_upper_limit"]:.2f} N',
                                f'  Lower Limit: {threshold_stats["force_lower_limit"]:.2f} N',
                                f'  Violations: {threshold_stats["force_violations"]} ({force_pct:.2f}%)',
                                ''
                            ])
                        else:
                            metadata_lines.extend(['Upper Force Thresholds: DISABLED', ''])
                        
                        if threshold_stats['stiffness_enabled']:
                            stiffness_pct = (threshold_stats["stiffness_violations"] / len(cycles) * 100) if len(cycles) > 0 else 0
                            metadata_lines.extend([
                                f'Loss of Stiffness Thresholds: ENABLED',
                                f'  Upper Limit: {threshold_stats["stiffness_upper_limit"]:.2f} %',
                                f'  Lower Limit: {threshold_stats["stiffness_lower_limit"]:.2f} %',
                                f'  Violations: {threshold_stats["stiffness_violations"]} ({stiffness_pct:.2f}%)',
                                ''
                            ])
                        else:
                            metadata_lines.extend(['Loss of Stiffness Thresholds: DISABLED', ''])
                    
                    # Data range summary
                    metadata_lines.extend([
                        'Data Ranges:',
                        '-' * 70,
                        f'Force Lower: [{min(force_lower):.2f}, {max(force_lower):.2f}] N',
                        f'Force Upper: [{min(force_upper):.2f}, {max(force_upper):.2f}] N',
                        f'Travel at Upper: [{min(travel_at_upper):.4f}, {max(travel_at_upper):.4f}] mm',
                        f'Travel 1: [{min(travel_1):.4f}, {max(travel_1):.4f}] mm',
                        f'Travel 2: [{min(travel_2):.4f}, {max(travel_2):.4f}] mm',
                        f'Loss of Stiffness: [{min(loss_of_stiffness):.2f}, {max(loss_of_stiffness):.2f}] %',
                        '',
                        '',
                        'Generated by: Fatigue Tester Data Acquisition System v2.2'
                    ])
                    
                    metadata_text = '\n'.join(metadata_lines)
                    ax4.text(0.1, 0.9, metadata_text, transform=ax4.transAxes,
                            fontsize=10, verticalalignment='top', fontfamily='monospace')
                    
                    pdf.savefig(fig4, bbox_inches='tight')
                    plt.close(fig4)
                
                # Set PDF metadata
                d = pdf.infodict()
                d['Title'] = 'Fatigue Test Results'
                d['Author'] = 'Fatigue Tester System v2.2'
                d['Subject'] = 'Test Data Visualization'
                d['Keywords'] = 'Fatigue Testing, Data Acquisition'
                d['Creator'] = 'Fatigue Tester Data Acquisition System'
                d['Producer'] = 'Matplotlib PDF Backend'
                if log_filename:
                    d['Comments'] = f'Data from: {log_filename}'
            
            return True
            
        except Exception as e:
            print(f"Error exporting to PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def export_to_png(self, filepath_prefix: str) -> bool:
        """
        Export each plot as a separate PNG file
        
        Args:
            filepath_prefix: Prefix for output PNG files (e.g., 'plot' -> 'plot_forces.png')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get data from plotter
            cycles = list(self.plotter.cycles)
            force_lower = list(self.plotter.force_lower)
            force_upper = list(self.plotter.force_upper)
            travel_at_upper = list(self.plotter.travel_at_upper)
            loss_of_stiffness = list(self.plotter.loss_of_stiffness)
            
            if not cycles:
                return False
            
            # Plot 1: Forces
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            ax1.plot(cycles, force_lower, 'b-', label='Lower Force [N]')
            ax1.plot(cycles, force_upper, 'r-', label='Upper Force [N]')
            ax1.set_xlabel('Cycles')
            ax1.set_ylabel('Force [N]')
            ax1.set_title('Forces vs Cycles')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            fig1.savefig(f'{filepath_prefix}_forces.png', dpi=300, bbox_inches='tight')
            plt.close(fig1)
            
            # Plot 2: Travel
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            ax2.plot(cycles, travel_at_upper, 'g-', label='Travel at Upper [mm]')
            ax2.set_xlabel('Cycles')
            ax2.set_ylabel('Travel [mm]')
            ax2.set_title('Travel vs Cycles')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            fig2.savefig(f'{filepath_prefix}_travel.png', dpi=300, bbox_inches='tight')
            plt.close(fig2)
            
            # Plot 3: Loss of Stiffness
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            ax3.plot(cycles, loss_of_stiffness, 'orange', label='Loss of Stiffness [%]')
            ax3.set_xlabel('Cycles')
            ax3.set_ylabel('Loss of Stiffness [%]')
            ax3.set_title('Loss of Stiffness vs Cycles')
            ax3.grid(True, alpha=0.3)
            ax3.legend()
            fig3.savefig(f'{filepath_prefix}_stiffness.png', dpi=300, bbox_inches='tight')
            plt.close(fig3)
            
            return True
            
        except Exception as e:
            print(f"Error exporting to PNG: {e}")
            return False
