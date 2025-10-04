import SwiftUI

struct StandingsDashboardView: View {
    @EnvironmentObject private var viewModel: StandingsViewModel
    @State private var selectedTeam: TeamStanding?
    @Namespace private var animation

    var body: some View {
        NavigationStack {
            ZStack {
                backgroundGradient
                    .ignoresSafeArea()

                ScrollView(showsIndicators: false) {
                    VStack(alignment: .leading, spacing: 28) {
                        StandingsHeaderView(
                            season: viewModel.season,
                            bestTeam: viewModel.bestWinPercentageTeam,
                            hottestTeam: viewModel.hottestStreakTeam,
                            topRunDifferentialTeam: viewModel.bestRunDifferentialTeam
                        )
                        filterPanel

                        if viewModel.filteredSections.isEmpty {
                            emptyState
                        } else {
                            LazyVStack(spacing: 28) {
                                ForEach(viewModel.filteredSections) { section in
                                    StandingsSectionView(
                                        section: section,
                                        favorites: viewModel.favorites,
                                        onFavoriteToggle: { team in
                                            withAnimation(.spring(response: 0.4, dampingFraction: 0.7)) {
                                                viewModel.toggleFavorite(for: team)
                                            }
                                        },
                                        onTeamSelected: { team in
                                            withAnimation(.easeInOut(duration: 0.2)) {
                                                selectedTeam = team
                                            }
                                        }
                                    )
                                }
                            }
                        }
                    }
                    .padding(.horizontal, 20)
                    .padding(.vertical, 32)
                }
                .refreshable {
                    await viewModel.refresh()
                }
                .overlay(alignment: .top) {
                    if let message = viewModel.errorMessage {
                        errorBanner(message: message)
                            .transition(.move(edge: .top).combined(with: .opacity))
                    }
                }

                if viewModel.isLoading {
                    ProgressView("Loading Standings")
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        .padding()
                        .background(RoundedRectangle(cornerRadius: 16).fill(Color.black.opacity(0.6)))
                }
            }
            .navigationTitle("")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    seasonMenu
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        Task { await viewModel.refresh() }
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }
                    .tint(.white)
                }
            }
            .sheet(item: $selectedTeam) { team in
                TeamDetailView(team: team, isFavorite: viewModel.favorites.contains(team.id)) {
                    viewModel.toggleFavorite(for: team)
                }
                .presentationDetents([.medium, .large])
            }
        }
    }

    private var backgroundGradient: LinearGradient {
        LinearGradient(
            colors: [Color(red: 10/255, green: 24/255, blue: 61/255), Color(red: 3/255, green: 7/255, blue: 18/255)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }

    private var filterPanel: some View {
        VStack(alignment: .leading, spacing: 18) {
            StandingsSearchBar(text: $viewModel.searchText)

            Picker("League", selection: $viewModel.selectedLeague) {
                ForEach(LeagueFilter.allCases) { filter in
                    Text(filter.title).tag(filter)
                }
            }
            .pickerStyle(.segmented)

            if !viewModel.availableDivisionFilters.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        divisionChip(title: "All Divisions", isSelected: viewModel.selectedDivisionID == nil) {
                            withAnimation(.spring(response: 0.35, dampingFraction: 0.7)) {
                                viewModel.selectedDivisionID = nil
                            }
                        }
                        ForEach(viewModel.availableDivisionFilters) { descriptor in
                            divisionChip(title: descriptor.name, isSelected: viewModel.selectedDivisionID == descriptor.id) {
                                withAnimation(.spring(response: 0.35, dampingFraction: 0.7)) {
                                    viewModel.selectedDivisionID = descriptor.id
                                }
                            }
                        }
                    }
                    .padding(.horizontal, 4)
                }
            }

            HStack(spacing: 12) {
                Menu {
                    Picker("Sort", selection: $viewModel.sortOption) {
                        ForEach(SortOption.allCases) { option in
                            Label(option.title, systemImage: option.systemImage).tag(option)
                        }
                    }
                } label: {
                    Label("Sort: \(viewModel.sortOption.title)", systemImage: "arrow.up.arrow.down")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.white)
                        .padding(.horizontal, 14)
                        .padding(.vertical, 10)
                        .background(
                            Capsule(style: .continuous)
                                .fill(Color.white.opacity(0.12))
                        )
                }

                Toggle(isOn: $viewModel.showFavoritesOnly) {
                    Label("Favorites", systemImage: viewModel.showFavoritesOnly ? "star.fill" : "star")
                }
                .toggleStyle(.switch)
                .tint(.yellow)
                .labelStyle(.titleAndIcon)
                .foregroundStyle(.white)

                if filtersActive {
                    Button("Reset") {
                        withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) {
                            viewModel.clearFilters()
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.white.opacity(0.15))
                }
            }
        }
        .padding(24)
        .background(
            RoundedRectangle(cornerRadius: 32, style: .continuous)
                .fill(Color.white.opacity(0.08))
                .overlay(
                    RoundedRectangle(cornerRadius: 32, style: .continuous)
                        .stroke(.white.opacity(0.12), lineWidth: 1)
                )
        )
    }

    private var filtersActive: Bool {
        !viewModel.searchText.isEmpty ||
        viewModel.selectedLeague != .all ||
        viewModel.selectedDivisionID != nil ||
        viewModel.showFavoritesOnly ||
        viewModel.sortOption != .divisionRank
    }

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "sparkles")
                .font(.system(size: 42))
                .foregroundStyle(.white.opacity(0.75))
            Text("No teams match your filters just yet.")
                .font(.headline)
                .foregroundStyle(.white)
            Text("Try clearing or adjusting your filters to see more clubs.")
                .font(.subheadline)
                .multilineTextAlignment(.center)
                .foregroundStyle(.white.opacity(0.7))
        }
        .padding(32)
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .fill(Color.white.opacity(0.08))
        )
    }

    private func divisionChip(title: String, isSelected: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .padding(.horizontal, 14)
                .padding(.vertical, 10)
                .background(
                    Capsule(style: .continuous)
                        .fill(isSelected ? Color.white.opacity(0.24) : Color.white.opacity(0.08))
                )
                .overlay(
                    Capsule(style: .continuous)
                        .stroke(isSelected ? Color.white.opacity(0.7) : Color.white.opacity(0.15), lineWidth: 1)
                )
        }
        .buttonStyle(.plain)
        .foregroundStyle(.white)
    }

    private func errorBanner(message: String) -> some View {
        HStack(spacing: 12) {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundStyle(.yellow)
            Text(message)
                .foregroundStyle(.white)
                .font(.subheadline)
            Spacer()
            Button("Dismiss") {
                withAnimation(.easeInOut) {
                    viewModel.errorMessage = nil
                }
            }
            .buttonStyle(.borderedProminent)
            .tint(.white.opacity(0.1))
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(Color.black.opacity(0.6))
        )
        .padding(.top, 12)
        .padding(.horizontal, 20)
    }

    private var seasonMenu: some View {
        Menu {
            Picker("Season", selection: $viewModel.season) {
                ForEach(viewModel.availableSeasons, id: \.self) { season in
                    Text(String(season)).tag(season)
                }
            }
        } label: {
            Label("Season \(viewModel.season)", systemImage: "calendar")
                .foregroundStyle(.white)
        }
    }
}

struct StandingsDashboardView_Previews: PreviewProvider {
    static var previews: some View {
        StandingsDashboardView()
            .environmentObject(StandingsViewModel())
            .preferredColorScheme(.dark)
    }
}
