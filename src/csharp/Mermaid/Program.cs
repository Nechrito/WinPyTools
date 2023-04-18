using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using Mermaid.Scripts;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.MSBuild;

namespace Mermaid;

internal class Program
{
    internal static async Task Main(string[] args)
    {
        var solutionPath = args != null && args.Length >= 1 ? args[0] : "C:\\Apps\\The-Prophecy-of-Hank\\HandyHank\\Assets\\HandyHank\\Scripts\\Runtime";

        var outputFile = args != null && args.Length >= 2 ? args[1] : "Mermaid.mmd";

        outputFile = Path.Combine(Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location), outputFile);
        Console.WriteLine($"Solution Path: {solutionPath} Output File: {outputFile}");

        if (!Directory.Exists(solutionPath))
        {
            Console.WriteLine($"{solutionPath} does not exist");
            return;
        }

        var dump = new ClassDiagram(solutionPath, outputFile);
        await dump.DumpMermaid();

        var folder_optimizer = new FolderStructureOptimizer(solutionPath, outputFile);
        folder_optimizer.FindOptimalFolderStructure();

        //DumpMermaid(args);
    }



    private static void DumpMermaid(string[] args)
    {
        var solutionPath = args[0];
        var outputFile = args[1];
        outputFile = Path.Combine(Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location), outputFile);

        Console.WriteLine($"Solution Path: {solutionPath}");
        Console.WriteLine($"Output File: {outputFile}");

        if (!Directory.Exists(solutionPath))
        {
            Console.WriteLine($"{solutionPath} does not exist");
            return;
        }

        var relationships = new List<Tuple<string, string, string>>();
        var scriptCount = 0;

        foreach (var file in Directory.GetFiles(solutionPath, "*.cs", SearchOption.AllDirectories))
        {
            if (file.Contains(".meta"))
                continue;

            relationships.AddRange(ParseCSharpCode(file));

            scriptCount++;
        }

        Console.WriteLine($"Found {scriptCount} scripts");

        var mermaid = BuildMermaid(relationships);

        //Console.WriteLine(mermaid);

        File.WriteAllText(outputFile, mermaid);

        //var dump = new Mermaid(outputFile, mermaid);

    }

    // private static void Dump(string outputFile, string mermaid)
    // {
    //     throw new NotImplementedException();
    // }

    private static string BuildMermaid(List<Tuple<string, string, string>> relationships)
    {
        var classToFolderMap = new Dictionary<string, string>();

        foreach (var relationship in relationships)
        {
            var className = relationship.Item1;
            var baseClassName = relationship.Item2;

            if (!classToFolderMap.ContainsKey(className))
            {
                classToFolderMap.Add(className, className);
            }

            if (!classToFolderMap.ContainsKey(baseClassName))
            {
                classToFolderMap.Add(baseClassName, baseClassName);
            }
        }

        var mermaid = new StringBuilder();
        mermaid.AppendLine("flowchart RL");
        mermaid.AppendLine("classDef default fill:#ffffffc9,stroke:#109868,stroke-width:3px");

        foreach (var relationship in relationships)
        {
            var className = relationship.Item1;
            var baseClassName = relationship.Item2;
            var classParameters = relationship.Item3;

            // if (className.StartsWith("I"))
            // {
            //     continue;
            // }

            // if (baseClassName.StartsWith("I"))
            // {
            //     continue;
            // }

            var classNameFolder = classToFolderMap[className];
            var baseClassNameFolder = classToFolderMap[baseClassName];

            if (classNameFolder == baseClassNameFolder)
            {
                var temp = !string.IsNullOrEmpty(baseClassName) ? $"  {className} --> {baseClassName}" : $"  {className}";
                mermaid.AppendLine($"{temp}");
            }
            else
            {
                var temp = !string.IsNullOrEmpty(baseClassNameFolder) ? $"  {classNameFolder} --> {baseClassNameFolder}" : classNameFolder; //$"classDef {classNameFolder} fill:#f96";
                mermaid.AppendLine($"{temp}");
            }
        }

        // TODO: Ensure distinct lines only
        var text = mermaid.ToString();

        return text.Split('\n').Distinct().Aggregate((a, b) => a + "\n" + b);

        //return Regex.Replace(mermaid.ToString(), @"(.*)\r?\n\1", "$1");
    }

    private static string ParseClassParameters(ClassDeclarationSyntax classDeclaration)
    {
        var constructor = classDeclaration.DescendantNodes().OfType<ConstructorDeclarationSyntax>().FirstOrDefault();

        if (constructor != null)
        {
            var parameters = constructor.ParameterList.Parameters;
            return string.Join(", ", parameters);
        }

        return string.Empty;
    }

    private static List<Tuple<string, string, string>> ParseCSharpCode(string file)
    {
        var relationships = new List<Tuple<string, string, string>>();
        var tree = CSharpSyntaxTree.ParseText(File.ReadAllText(file));
        var root = tree.GetRoot();
        var classes = root.DescendantNodes().OfType<ClassDeclarationSyntax>();

        foreach (var @class in classes)
        {
            var baseList = @class.BaseList;

            if (baseList != null)
            {
                foreach (var type in baseList.Types)
                {
                    var baseClass = type.Type.ToString();
                    var classParameters = ParseClassParameters(@class);

                    if (@class.Identifier.Text.Contains('@'))
                    {
                        continue;
                    }

                    baseClass = baseClass.Replace('<', '[').Replace('>', ']');

                    baseClass = Regex.Replace(baseClass, @"(.*)\[(.*)\]", "$1");

                    baseClass = Regex.Replace(baseClass, @"(.*)\[(.*)", "$1");

                    if (baseClass == "MonoBehaviour" || baseClass == "ScriptableObject" || baseClass == "SerializedScriptableObject" || baseClass == "SerializedMonoBehaviour")
                    {
                        baseClass = string.Empty;
                    }

                    relationships.Add(new Tuple<string, string, string>(@class.Identifier.Text, baseClass, classParameters));
                }
            }
        }

        return relationships;
    }
}