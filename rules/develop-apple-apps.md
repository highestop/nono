# Develop Apple apps

## Keep the app small and focused

- Start with the smallest complete workflow. Give each screen a clear primary action and useful defaults. Add a setting, step, or confirmation when it helps someone make a real decision.
- Use the simplest implementation that handles the expected inputs and failures. Reuse shared logic where the behavior is the same. Add dependencies or abstractions for current needs.
- Choose and document the minimum OS for each target before implementation. Base it on the native capabilities the app needs and the devices it serves. Use one native interface path per platform by default. Add a fallback only for a concrete support commitment that can be tested.
- Treat saved data and file formats as product contracts. Plan any required data migration when changing a released app.

## Make the interface feel native

- Start with system navigation, controls, file pickers, dialogs, and settings. Use SwiftUI where it fits and UIKit or AppKit when they provide the behavior the workflow needs.
- Use native Liquid Glass for the navigation and control layer on supported platforms. Keep the content layer readable with standard surfaces. Prefer system corners, transitions, and feedback. [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass) · [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- Use the app's own palette and shapes consistently. Keep motion short and tied to a change in state. Respect system appearance, text size, accessibility, and motion preferences.

## Fit the platform

- **iOS.** Keep primary touch actions within reach and adapt to safe areas and text size. [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- **iPadOS.** Lay out content for the available window size. Support the keyboard and pointer where they help the task. [Designing for iPadOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ipados)
- **macOS.** Use familiar windows, menus, and keyboard shortcuts for common commands. [Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos)
- **tvOS.** Design for the Siri Remote and a distant display. Keep the focused item obvious and navigation predictable. [Designing for tvOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-tvos)

## Read before designing or changing the interface

- Consult the current Apple Human Interface Guidelines for the target platform and the Apple documentation for the APIs you intend to use. [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- Read the installed `ui-ux-pro-max` skill for layout, interaction, and accessibility review. Apply its suggestions in the context of the target platform's Apple guidance.
- Use `design-app-icon` as an optional reference for icon exploration or asset preparation. Choose a mark that fits the app's name and purpose, and follow Apple's icon guidance for the target. [App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)

Build for the supported targets and verify the main workflow and relevant failure or retry states. Check material, motion, and input behavior on the target platform when evaluating the visual experience.

## Reuse one Preview app during development

- Use one fixed Preview app name, install path, and bundle identifier per project. Quit the running app before updating that same app in place; do not create a new app identity for every build or test run.
- Keep only one Preview app instance open. Quit it when verification finishes, and reopen it only when another check needs it.
- Reuse the user's existing authorization for Preview app testing and computer use. Do not ask for permission again for each build or test run; honor any approval enforced by the host.
- Keep test data and run evidence isolated even though the app identity stays fixed. Preserve the tested source revision and build record for each run.
