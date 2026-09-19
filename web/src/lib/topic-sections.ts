export type TopicSection = { id: string; label: string; available: boolean };
export function visibleSections(sections: readonly TopicSection[]): TopicSection[] {
  return sections.filter((section) => section.available && Boolean(section.id) && Boolean(section.label));
}
