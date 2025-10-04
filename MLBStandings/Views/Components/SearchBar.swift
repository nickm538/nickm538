import SwiftUI

struct StandingsSearchBar: View {
    @Binding var text: String
    @FocusState private var isFocused: Bool

    var placeholder: String = "Search teams"

    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 16, weight: .semibold))
                .foregroundStyle(.secondary)

            TextField(placeholder, text: $text)
                .textInputAutocapitalization(.never)
                .disableAutocorrection(true)
                .focused($isFocused)

            if !text.isEmpty {
                Button {
                    withAnimation(.easeOut(duration: 0.2)) {
                        text = ""
                    }
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundStyle(.secondary)
                        .font(.system(size: 16, weight: .semibold))
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 12)
        .background(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .fill(.ultraThinMaterial)
                .shadow(color: .black.opacity(0.08), radius: 12, x: 0, y: 8)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .strokeBorder(.white.opacity(0.2), lineWidth: 1)
        )
        .onTapGesture {
            isFocused = true
        }
        .animation(.easeInOut(duration: 0.2), value: text)
    }
}

struct StandingsSearchBar_Previews: PreviewProvider {
    static var previews: some View {
        ZStack {
            Color(.systemIndigo).opacity(0.2).ignoresSafeArea()
            StandingsSearchBar(text: .constant("Yankees"))
                .padding()
        }
    }
}
